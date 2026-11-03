// Render retained press layouts with the original approved media kit.
// PLAYWRIGHT_MODULE and CHROME_EXECUTABLE may point to an existing installation.
import { mkdtemp, mkdir, readdir, symlink, copyFile, rm, writeFile } from 'node:fs/promises';
import { resolve, join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const kit = resolve(process.argv[2]);
const output = join(root, `dist/assets/press/${process.env.PRESS_EDITION || '2026-11-03-v22'}/01-documents`);
const temp = await mkdtemp(join(tmpdir(), 'atomic-press-'));
await mkdir(join(temp, '01-documents'));
for (const name of await readdir(kit)) {
  if (name !== '01-documents') await symlink(join(kit, name), join(temp, name));
}
const files = await readdir(join(root, 'content/press-documents'));
for (const name of files) await copyFile(join(root, 'content/press-documents', name), join(temp, '01-documents', name));
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser = await chromium.launch({
  executablePath: process.env.CHROME_EXECUTABLE || undefined,
  headless: true,
  args: ['--no-sandbox'],
});
const report = [];
try {
  const page = await browser.newPage();
  await page.emulateMedia({ media: 'print' });
  for (const name of files.filter(n => n.endsWith('.html')).sort()) {
    await page.goto('file://' + join(temp, '01-documents', name));
    await page.evaluate(() => document.fonts.ready);
    const checks = await page.evaluate(() => ({
      pages: document.querySelectorAll('.page').length,
      missing: [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.src),
      overflow: [...document.querySelectorAll('.page')].flatMap((p, index) => {
        const content = p.querySelector('.page-content');
        const footer = p.querySelector('.footer');
        return content && footer && content.getBoundingClientRect().bottom > footer.getBoundingClientRect().top - 8 ? [index + 1] : [];
      }),
    }));
    if (checks.missing.length || checks.overflow.length) throw new Error(name + ': ' + JSON.stringify(checks));
    await page.pdf({ path: join(output, name.replace('.html', '.pdf')), format: 'A4', printBackground: true, preferCSSPageSize: true });
    report.push({ name, ...checks });
    console.log('Verified and rendered ' + name);
  }
  await writeFile('/tmp/atomic-press-render-check.json', JSON.stringify(report, null, 2));
} finally {
  await browser.close();
  await rm(temp, { recursive: true, force: true });
}
