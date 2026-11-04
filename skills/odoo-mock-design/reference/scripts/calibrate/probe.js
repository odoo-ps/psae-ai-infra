// Computed-style / DOM probe — the numbers behind a visual comparison.
//   node probe.js real <odoo-path> '<["css", ...]>' [--html] [--steps '<json>']
//   node probe.js file <page.html> '<["css", ...]>' [--html] [--hash screen-id]
// Prints JSON {selector: [{rect, font-*, color, background-color, border-*, radius,
// padding, margin, size, gap, shadow, html?} × up to 3 matches]}.
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const os = require('os');
const path = require('path');
const C = require('./_common');

const PROPS = ['display', 'position', 'font-family', 'font-size', 'font-weight', 'line-height', 'color',
  'background-color', 'border-top', 'border-right', 'border-bottom', 'border-left', 'border-radius', 'padding',
  'margin', 'width', 'height', 'gap', 'box-shadow', 'text-transform', 'letter-spacing', 'opacity'];
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > -1 ? process.argv[i + 1] : d; };

(async () => {
  const [mode, target, selArg] = process.argv.slice(2, 5);
  if (!selArg || !['real', 'file'].includes(mode)) { console.error('usage: see header'); process.exit(2); }
  const sels = JSON.parse(selArg);
  const wantHtml = process.argv.includes('--html');
  if (!C.CHROME) { console.error('No Chrome found; set CHROME_PATH'); process.exit(2); }
  const browser = await puppeteer.launch({ executablePath: C.CHROME, headless: 'new', args: ['--allow-file-access-from-files'] });
  let page;
  if (mode === 'real') {
    await C.login(browser);
    page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900 });
    await page.goto(C.ODOO_URL + target, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await C.settle(page);
    await C.runSteps(page, JSON.parse(arg('--steps', '[]')));
  } else {
    page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900 });
    const staged = C.stagePage(target, path.join(os.tmpdir(), 'mock_calibrate_stage'));
    const hash = arg('--hash', null);
    await page.goto('file://' + staged + (hash ? '#' + hash : ''), { waitUntil: 'load' });
    await C.sleep(500);
  }
  const result = await page.evaluate((sels, PROPS, wantHtml) => {
    const out = {};
    for (const s of sels) {
      out[s] = [...document.querySelectorAll(s)].filter((e) => e.getClientRects().length).slice(0, 3).map((e) => {
        const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
        const o = { rect: [r.x, r.y, r.width, r.height].map(Math.round) };
        for (const p of PROPS) {
          const v = cs.getPropertyValue(p);
          if (v && !['none', 'normal', '0px', 'auto', 'rgba(0, 0, 0, 0)'].includes(v)) o[p] = v;
        }
        if (wantHtml) o.html = e.outerHTML.replace(/\s+/g, ' ').slice(0, 2500);
        return o;
      });
    }
    return out;
  }, sels, PROPS, wantHtml);
  console.log(JSON.stringify(result, null, 1));
  await browser.close();
})();
