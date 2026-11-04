// Shared config for the calibration kit. Override with environment variables.
const fs = require('fs');
const path = require('path');

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
].filter(Boolean);

module.exports = {
  ODOO_URL: process.env.ODOO_URL || 'http://127.0.0.1:8069',
  LOGIN: process.env.ODOO_LOGIN || 'admin',
  PASSWORD: process.env.ODOO_PASSWORD || 'admin',
  CHROME: CHROME_CANDIDATES.find((p) => fs.existsSync(p)),
  CATALOG: path.resolve(__dirname, '..', '..', 'catalog'),
  sleep: (ms) => new Promise((r) => setTimeout(r, ms)),
  withTimeout: (p, ms) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), ms))]),

  async login(browser) {
    const page = await browser.newPage();
    await page.goto(module.exports.ODOO_URL + '/web/login', { waitUntil: 'networkidle2' });
    await page.type('input[name=login]', module.exports.LOGIN);
    await page.type('input[name=password]', module.exports.PASSWORD);
    await Promise.all([page.waitForNavigation({ waitUntil: 'networkidle2' }), page.keyboard.press('Enter')]);
    await page.close();
  },

  async settle(page) {
    try { await page.waitForNetworkIdle({ idleTime: 600, timeout: 6000, concurrency: 2 }); } catch (e) {}
    try { await page.waitForSelector('.o_action_manager .o_view_controller, .o_home_menu, .o_action_manager .o_form_view', { timeout: 8000 }); } catch (e) {}
    await module.exports.sleep(1200);
  },

  async runSteps(page, steps) {
    const log = [];
    for (const st of steps || []) {
      if (st.click) {
        const el = await page.$(st.click);
        if (el) await el.click(); else log.push('selector not found ' + st.click);
      } else if (st.clickText) {
        const ok = await page.evaluate((t, w) => {
          const root = w ? document.querySelector(w) : document;
          if (!root) return false;
          const els = [...root.querySelectorAll('button, a, span, div, li, .dropdown-item')]
            .filter((e) => e.offsetParent !== null && e.textContent.trim() === t);
          if (!els.length) return false;
          els[els.length - 1].click();
          return true;
        }, st.clickText, st.within || null);
        if (!ok) log.push('text not found ' + st.clickText);
      } else if (st.press) {
        await page.keyboard.press(st.press);
      }
      await module.exports.settle(page);
    }
    return log;
  },

  // Stage a catalog-based page so `assets/...` resolves to the LIVE catalog and
  // a literal <!-- SPRITE --> (or a page with no inline <symbol>) gets both sprites.
  stagePage(src, stageDir) {
    fs.mkdirSync(stageDir, { recursive: true });
    const assets = path.join(stageDir, 'assets');
    if (!fs.existsSync(assets)) fs.symlinkSync(module.exports.CATALOG, assets);
    let html = fs.readFileSync(src, 'utf8');
    // The staged copy lives in a temp dir, so relative links (e.g. a calibration
    // page's ../../catalog/odoo.css) would break: make every relative href/src
    // absolute against the SOURCE page's folder. `assets/...` stays relative —
    // it resolves through the staged assets → catalog symlink below.
    const srcDir = path.dirname(path.resolve(src));
    html = html.replace(/\b(href|src)="(?!https?:|file:|data:|#|\/|assets\/)([^"]+)"/g,
      (m, attr, rel) => `${attr}="file://${path.resolve(srcDir, rel)}"`);
    const C = module.exports.CATALOG;
    const sprite = fs.readFileSync(path.join(C, 'icons.svg'), 'utf8') + '\n' + fs.readFileSync(path.join(C, 'app-icons.svg'), 'utf8');
    if (html.includes('<!-- SPRITE -->')) html = html.replace('<!-- SPRITE -->', sprite);
    else if (!html.includes('<symbol')) html = html.replace(/<body[^>]*>/, (m) => m + '\n' + sprite);
    const staged = path.join(stageDir, '_staged_' + path.basename(src));
    fs.writeFileSync(staged, html);
    return staged;
  },
};
