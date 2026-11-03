// Browser checks for shared branding and responsive navigation; no form submission.
import {mkdir,writeFile} from 'node:fs/promises';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base=process.env.SITE_BASE || 'http://127.0.0.1:4185';
const output=process.env.BRAND_CHECK_OUTPUT || '/tmp/atomic-brand-check';
await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,...(process.env.CHROME_BIN?{executablePath:process.env.CHROME_BIN}:{}),args:['--no-sandbox']});
const report=[];
try {
  const page=await browser.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  for(const width of [1440,768,390,360]){
    await page.setViewportSize({width,height:1000});
    for(const path of ['/','/pricing/','/docs/','/solutions/','/about/','/early-access/','/press/']){
      await page.goto(base+path,{waitUntil:'domcontentloaded'});
      await page.evaluate(()=>document.fonts.ready);
      const state=await page.evaluate(()=>{
        const brand=document.querySelector('.site-header .brand');
        const logo=brand.querySelector('img');
        const rect=brand.getBoundingClientRect();
        const actions=document.querySelector('.header-actions').getBoundingClientRect();
        const footer=document.querySelector('.site-footer .brand img');
        return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
          logo:logo.getAttribute('src'),loaded:logo.complete&&logo.naturalWidth>0,
          footer:footer.getAttribute('src'),logoWidth:rect.width,logoHeight:rect.height,
          overlap:rect.right>actions.left,social:document.querySelector('meta[property="og:image"]').content};
      });
      if(state.scrollWidth>width||!state.loaded||state.overlap||state.logo!=='/assets/atomic-logo-lowercase-v3.svg'||state.footer!==state.logo||state.logoWidth<100||state.logoHeight>60)throw Error(path+' '+JSON.stringify(state));
      if(!state.social.includes(path==='/press/'?'2026-11-03-v17':'atomic-social-v5.png'))throw Error('Stale social card: '+path);
      if(path==='/'&&(width===1440||width===390))await page.screenshot({path:`${output}/home-${width}.png`});
      if(path==='/press/'&&width===1440){await page.locator('#logos').scrollIntoViewIfNeeded();await page.screenshot({path:`${output}/logos-desktop.png`});}
      if(width===390&&path==='/'){
        const toggle=page.locator('.menu-toggle');await toggle.click();
        if(!await page.locator('#mobile-nav').isVisible())throw Error('Mobile navigation did not open');
        await toggle.click();
      }
      report.push({path,...state});
    }
  }
  if(errors.length)throw Error(errors.join('\n'));
  await writeFile(output+'/report.json',JSON.stringify({report,errors},null,2));
  console.log(`Passed branding and layout checks on ${report.length} page/viewport combinations.`);
} finally {await browser.close();}
