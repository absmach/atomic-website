// Render the social preview from the exact supplied SVG and bundled font.
// Requires Playwright and Chromium for authoring only; no website runtime dependency.
import {readFile,copyFile} from 'node:fs/promises';
import {join,resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const font=(await readFile(join(root,'dist/assets/fonts/manrope-latin.woff2'))).toString('base64');
const logo=(await readFile(join(root,'dist/assets/atomic-logo-lowercase-v3.svg'))).toString('base64');
const browser=await chromium.launch({headless:true,...(process.env.CHROME_BIN?{executablePath:process.env.CHROME_BIN}:{}),args:['--no-sandbox']});
try {
  const page=await browser.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});
  await page.setContent(`<!doctype html><html><head><style>
  @font-face{font-family:Manrope;src:url(data:font/woff2;base64,${font});font-weight:200 800}
  *{box-sizing:border-box}body{margin:0;width:1200px;height:630px;padding:62px 76px;background:radial-gradient(ellipse at 16% 110%,#d9caffbb,transparent 68%),radial-gradient(ellipse at 100% 0%,#ffdfd177,transparent 55%),#fbfaf8;color:#221c30;font-family:Manrope,Arial,sans-serif}
  header{display:flex;align-items:center;justify-content:space-between}img{width:440px;height:auto;display:block}.url{font-size:27px;letter-spacing:-.6px;color:#625971}h1{font-size:84px;letter-spacing:-4px;line-height:1.15;font-weight:650;margin:103px 0 0;white-space:nowrap}h1 span{color:#6842ee}
  </style></head><body><header><img src="data:image/svg+xml;base64,${logo}" alt="Atomic"><span class="url">atomicapp.dev</span></header><h1>Imagine it. <span>Build it.</span></h1></body></html>`);
  await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});
  const output=join(root,'dist/assets/atomic-social-v7.png');
  await page.screenshot({path:output});
  // Keep previously advertised thumbnail URLs on the current identity too.
  // Crawlers with cached page metadata may still request one of these URLs.
  for(let version=1;version<=6;version++){
    await copyFile(output,join(root,`dist/assets/atomic-social-v${version}.png`));
  }
  console.log('Rendered atomic-social-v7.png (1200 × 630) and refreshed legacy thumbnail URLs v1–v6.');
} finally {await browser.close();}
