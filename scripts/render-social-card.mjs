// Render the social preview from the exact supplied SVG and bundled font.
// Requires Playwright and Chromium for authoring only; no website runtime dependency.
import {readFile} from 'node:fs/promises';
import {join,resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const font=(await readFile(join(root,'dist/assets/fonts/manrope-latin.woff2'))).toString('base64');
const logo=(await readFile(join(root,'dist/assets/atomic-logo-v2.svg'))).toString('base64');
const browser=await chromium.launch({headless:true,...(process.env.CHROME_BIN?{executablePath:process.env.CHROME_BIN}:{}),args:['--no-sandbox']});
try {
  const page=await browser.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});
  await page.setContent(`<!doctype html><html><head><style>
  @font-face{font-family:Manrope;src:url(data:font/woff2;base64,${font});font-weight:200 800}
  *{box-sizing:border-box}body{margin:0;width:1200px;height:630px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(ellipse at 24% 100%,#e2d8ff99,transparent 65%),radial-gradient(ellipse at 90% 0%,#ffdfd144,transparent 55%),#fbfaf8;color:#221c30;font-family:Manrope,Arial,sans-serif}
  img{width:550px;height:auto;display:block}h1{font-size:52px;letter-spacing:-2px;line-height:1.2;font-weight:650;margin:25px 0 0}
  </style></head><body><img src="data:image/svg+xml;base64,${logo}" alt="Atomic"><h1>Imagine it. Build it.</h1></body></html>`);
  await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});
  await page.screenshot({path:join(root,'dist/assets/atomic-social-v4.png')});
  console.log('Rendered dist/assets/atomic-social-v4.png (1200 × 630).');
} finally {await browser.close();}
