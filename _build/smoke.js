const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

const dir = process.argv[2] || 'site/dashboards';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.html'));

// Chart.js needs a canvas backend we don't have; stub getContext so the render
// code runs end to end without a real 2d context.
const stubCtx = new Proxy({}, {
  get: (t, k) => {
    if (k === 'canvas') return { style: {}, width: 600, height: 400 };
    if (k === 'measureText') return () => ({ width: 10, actualBoundingBoxLeft: 0, actualBoundingBoxRight: 10, actualBoundingBoxAscent: 5, actualBoundingBoxDescent: 2 });
    if (k === 'createLinearGradient') return () => ({ addColorStop() {} });
    if (k === 'getImageData') return () => ({ data: [] });
    return () => {};
  },
  set: () => true,
});

(async () => {
  let failures = 0;
  for (const f of files) {
    const html = fs.readFileSync(path.join(dir, f), 'utf8');
    const errors = [];
    const vc = new VirtualConsole();
    vc.on('jsdomError', e => {
      if (!/Not implemented|Could not parse CSS/.test(e.message)) errors.push(e.message.split('\n')[0]);
    });
    vc.on('error', (...a) => errors.push('console.error: ' + a.join(' ').slice(0, 200)));

    const dom = new JSDOM(html, { runScripts: 'dangerously', virtualConsole: vc, pretendToBeVisual: true });
    dom.window.HTMLCanvasElement.prototype.getContext = () => stubCtx;
    await new Promise(r => setTimeout(r, 400));

    const doc = dom.window.document;
    const text = doc.body.textContent.replace(/\s+/g, ' ');
    // A rendered page should have swapped its placeholder em-dashes for values.
    const emptyKpis = [...doc.querySelectorAll('[id]')].filter(
      el => el.children.length === 0 && el.textContent.trim() === '—').length;
    const tableRows = doc.querySelectorAll('tbody tr, table tr').length;

    console.log(
      `${errors.length ? 'FAIL' : ' ok '}  ${f.padEnd(34)} rows=${String(tableRows).padStart(5)}  unfilled=${String(emptyKpis).padStart(3)}  chars=${text.length}`);
    errors.slice(0, 4).forEach(e => console.log('        ! ' + e.slice(0, 180)));
    if (errors.length) failures++;
    dom.window.close();
  }
  process.exit(failures ? 1 : 0);
})();
