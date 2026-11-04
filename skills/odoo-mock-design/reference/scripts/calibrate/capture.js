// Capture REAL Odoo screens (the calibration ground truth).
// Usage: ODOO_URL=http://127.0.0.1:8399 node capture.js <outdir> [screen-name ...]
// Screens come from screens.json. One fresh tab per screen (a screen that opens
// a composer/dialog can otherwise block later navigations).
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const C = require('./_common');

(async () => {
  const out = process.argv[2];
  if (!out) { console.error('usage: node capture.js <outdir> [screen ...]'); process.exit(2); }
  if (!C.CHROME) { console.error('No Chrome found; set CHROME_PATH'); process.exit(2); }
  const only = process.argv.slice(3);
  const { screens } = JSON.parse(fs.readFileSync(path.join(__dirname, 'screens.json'), 'utf8'));
  fs.mkdirSync(out, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: C.CHROME, headless: 'new' });
  await C.login(browser);
  for (const s of screens) {
    if (only.length && !only.includes(s.name)) continue;
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });
    page.on('dialog', (d) => d.accept().catch(() => {}));
    try {
      await C.withTimeout((async () => {
        await page.goto(C.ODOO_URL + s.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await C.settle(page);
        const log = await C.runSteps(page, s.steps);
        await page.screenshot({ path: path.join(out, s.name + '.png') });
        console.log(`${s.name}: ok${log.length ? ' (' + log.join('; ') + ')' : ''}`);
      })(), 60000);
    } catch (e) {
      console.log(`${s.name}: ERROR ${e.message}`);
    }
    await page.close().catch(() => {});
  }
  await browser.close();
})();
