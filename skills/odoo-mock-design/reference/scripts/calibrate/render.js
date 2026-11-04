// Render a catalog-based page (or one element) against the LIVE catalog.
//   node render.js <page.html> <out.png> [--w 1440] [--h 900] [--full] [--selector css] [--hash screen-id]
const puppeteer = require('puppeteer-core');
const os = require('os');
const path = require('path');
const C = require('./_common');
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > -1 ? process.argv[i + 1] : d; };

(async () => {
  const [src, out] = process.argv.slice(2, 4);
  if (!out) { console.error('usage: node render.js <page.html> <out.png> [...]'); process.exit(2); }
  if (!C.CHROME) { console.error('No Chrome found; set CHROME_PATH'); process.exit(2); }
  const staged = C.stagePage(src, path.join(os.tmpdir(), 'mock_calibrate_stage'));
  const browser = await puppeteer.launch({ executablePath: C.CHROME, headless: 'new', args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage();
  await page.setViewport({ width: +arg('--w', 1440), height: +arg('--h', 900), deviceScaleFactor: 2 });
  const hash = arg('--hash', null);
  await page.goto('file://' + staged + (hash ? '#' + hash : ''), { waitUntil: 'load' });
  await C.sleep(600);
  const sel = arg('--selector', null);
  if (sel) {
    const el = await page.$(sel);
    if (!el) { console.error('selector not found: ' + sel); process.exit(3); }
    await el.screenshot({ path: out });
  } else {
    await page.screenshot({ path: out, fullPage: process.argv.includes('--full') });
  }
  await browser.close();
  console.log('wrote ' + out);
})();
