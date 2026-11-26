// CP-11, pasos de valores límite: ejecuta en el navegador y agrega el resultado a resultados.json
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const OUT = process.argv[2]; const URL = 'http://127.0.0.1:5000';
(async () => {
  const b = await chromium.launch(); const page = await (await b.newContext({ viewport: { width: 1280, height: 820 } })).newPage();
  await page.goto(URL + '/login'); await page.fill('[name=usuario]', 'admin'); await page.fill('[name=clave]', 'Admin2026!');
  await Promise.all([page.waitForNavigation(), page.click('button')]);
  const json = path.join(OUT, 'resultados.json'); const d = JSON.parse(fs.readFileSync(json));
  d.resultados = d.resultados.filter((r) => !/límite/.test(r.paso));
  const nuevos = [];
  for (const [nombre, regla, nom, desc] of [['Laura Pinto', '15/16 prácticas', 'limite_horas', 'Laura Pinto (aprobada, 20/15 h, saldo 0; valor límite): Generar certificado'],
    ['Raúl Mena', 'saldo pendiente de B/. 0.01', 'limite_saldo', 'Raúl Mena (aprobado, 20/16 h, debe B/. 0.01; valor límite): Generar certificado']]) {
    await page.goto(URL + '/alumnos');
    const [r] = await Promise.all([page.waitForNavigation(), page.locator('tr', { hasText: nombre }).locator('text=Generar certificado').click()]);
    const f = 'CP11_rechazo_' + nom + '.png'; await page.screenshot({ path: path.join(OUT, f), fullPage: true });
    const motivos = await page.locator('#ventana-motivos li').allInnerTexts();
    const ok = r.status() === 409 && motivos.join(' ').includes(regla);
    nuevos.push({ cp: 'CP-11', paso: desc, esperado: `HTTP 409 y motivo "${regla}"`, observado: `HTTP ${r.status()}; ${motivos.join(' | ')}`, ok, captura: f });
    console.log(ok ? 'OK' : 'FALLA', desc, '|', motivos.join(' | '));
  }
  const i = d.resultados.map((r) => r.cp).lastIndexOf('CP-11');
  d.resultados.splice(i + 1, 0, ...nuevos);
  fs.writeFileSync(json, JSON.stringify(d, null, 2)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
