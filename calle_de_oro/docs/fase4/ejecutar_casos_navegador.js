// Ejecuta los 12 casos de prueba de la Fase 4 en el navegador contra la app real y guarda evidencias.
// Uso: node ejecutar.js <carpeta_salida> <etiqueta>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = process.argv[2];
const ETIQ = process.argv[3] || 'ronda';
const URL = 'http://127.0.0.1:5000';
fs.mkdirSync(OUT, { recursive: true });
const resultados = [];

function reg(cp, paso, esperado, observado, ok, captura) {
  resultados.push({ cp, paso, esperado, observado, ok, captura });
  console.log(`${ok ? 'OK  ' : 'FALLA'} ${cp} | ${paso} | ${observado}`);
}

async function shot(page, nombre) {
  const f = `${nombre}.png`;
  await page.screenshot({ path: path.join(OUT, f), fullPage: true });
  return f;
}

async function login(page, u, c) {
  await page.goto(URL + '/logout');
  await page.goto(URL + '/login');
  await page.fill('[name=usuario]', u);
  await page.fill('[name=clave]', c);
  await Promise.all([page.waitForNavigation(), page.click('button')]);
}

async function enviar(page, selectorBoton) {
  const [resp] = await Promise.all([page.waitForNavigation(), page.click(selectorBoton)]);
  return resp ? resp.status() : 0;
}

const sinJS = (page) => page.evaluate(() => { window.validarFormulario = () => true; });
const texto = (page) => page.evaluate(() => document.body.innerText);
const errorDe = (page, campo) => page.textContent('#error-' + campo).then((t) => (t || '').trim());

async function abrirAlumno(page) {
  await page.goto(URL + '/alumnos');
  await page.click('text=+ Registrar alumno');
}
async function llenarAlumno(page, d) {
  await page.fill('[name=nombre]', d.nombre);
  await page.fill('[name=cedula]', d.cedula);
  await page.fill('[name=telefono]', d.telefono);
  await page.fill('[name=correo]', d.correo);
  await page.fill('[name=direccion]', d.direccion);
  await page.selectOption('[name=id_curso]', d.id_curso);
  await page.selectOption('[name=tipo_vehiculo]', d.tipo_vehiculo);
  await page.fill('[name=abono]', d.abono);
}
async function abrirPago(page) {
  await page.goto(URL + '/pagos');
  await page.click('text=+ Registrar pago');
}
async function llenarPago(page, idAlumno, monto, metodo, ref) {
  await page.selectOption('[name=id_alumno]', idAlumno);
  await page.fill('[name=monto]', monto);
  await page.selectOption('[name=metodo]', metodo);
  await page.fill('[name=referencia]', ref || '');
}
async function pdfTexto(page, ruta, nombre) {
  const r = await page.request.get(URL + ruta);
  const buf = await r.body();
  const f = path.join(OUT, nombre + '.pdf');
  fs.writeFileSync(f, buf);
  return { status: r.status(), tipo: r.headers()['content-type'], archivo: nombre + '.pdf', inicio: buf.slice(0, 4).toString() };
}

(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 820 } })).newPage();
  let t, s, c, e;

  // ================= CU-01 (Recepcionista) =================
  await login(page, 'recepcion', 'Recepcion2026!');
  const base = { nombre: 'María Fernández', cedula: '8-123-4567', telefono: '6000-1234', correo: 'maria@correo.com',
    direccion: 'Panamá, San Francisco', id_curso: '2', tipo_vehiculo: 'Manual', abono: '150' };

  // CP-01 Registro exitoso
  await abrirAlumno(page); await llenarAlumno(page, base);
  c = await shot(page, 'CP01_a_formulario');
  s = await enviar(page, 'text=Registrar e iniciar factura'); t = await texto(page);
  c = [c, await shot(page, 'CP01_b_registrado')];
  reg('CP-01', 'Registrar a María Fernández, Licencia B (B/. 220), abono B/. 150', 'Mensaje de éxito con FAC y REC, saldo B/. 70.00; aparece en la lista',
    `HTTP ${s}; ${(t.match(/Alumno María[^\n]*/) || ['(sin mensaje)'])[0]}`, s === 200 && /Saldo pendiente: B\/\. 70\.00/.test(t) && t.includes('8-123-4567'), c);

  // CP-02 Validación de campos (navegador y servidor)
  await abrirAlumno(page);
  await llenarAlumno(page, { ...base, nombre: 'Pedro', cedula: '123', telefono: '12', correo: 'pedro', direccion: 'Pa', cedula2: '' });
  await page.click('text=Registrar e iniciar factura');
  e = { nombre: await errorDe(page, 'nombre'), cedula: await errorDe(page, 'cedula'), telefono: await errorDe(page, 'telefono'), correo: await errorDe(page, 'correo') };
  c = [await shot(page, 'CP02_a_validacion_navegador')];
  reg('CP-02', 'Navegador: nombre sin apellido, cédula 123, teléfono 12, correo sin @', 'Campos en rojo con mensaje; el formulario no se envía',
    `Mensajes: ${Object.values(e).join(' | ')}; URL sigue en /alumnos`, e.nombre && e.cedula.startsWith('Cédula') && e.telefono.startsWith('Teléfono') && e.correo.startsWith('Correo') && page.url().endsWith('/alumnos'), c[0]);
  await sinJS(page);
  s = await enviar(page, 'text=Registrar e iniciar factura');
  e = { nombre: await errorDe(page, 'nombre'), cedula: await errorDe(page, 'cedula'), direccion: await errorDe(page, 'direccion') };
  c = await shot(page, 'CP02_b_validacion_servidor');
  reg('CP-02', 'Servidor: mismos datos con la validación del navegador desactivada', 'HTTP 422 y los mismos errores; no se guarda nada',
    `HTTP ${s}; ${Object.values(e).join(' | ')}`, s === 422 && e.cedula.startsWith('Cédula') && e.direccion !== '', c);

  // CP-03 Cédula repetida
  await abrirAlumno(page); await llenarAlumno(page, { ...base, nombre: 'Luis Prado', cedula: '8-902-1145', correo: 'luis@correo.com' });
  s = await enviar(page, 'text=Registrar e iniciar factura'); e = await errorDe(page, 'cedula');
  c = await shot(page, 'CP03_cedula_repetida');
  reg('CP-03', 'Registrar con la cédula 8-902-1145 (ya es de Mariela Vega)', 'HTTP 422 y "Ya existe un alumno con esta cédula."', `HTTP ${s}; ${e}`, s === 422 && e.includes('Ya existe'), c);

  // CP-04 Abono mínimo 50 % (valores límite)
  const d4 = { ...base, nombre: 'Rosa Díaz', cedula: '8-555-1010', correo: 'rosa@correo.com' };
  await abrirAlumno(page); await llenarAlumno(page, { ...d4, abono: '109.99' });
  await page.click('text=Registrar e iniciar factura'); e = await errorDe(page, 'abono');
  c = await shot(page, 'CP04_a_abono_109_99_navegador');
  reg('CP-04', 'Navegador: abono B/. 109.99 (49,99 % de B/. 220)', 'Error "El abono mínimo es B/. 110.00"', e, e.includes('110.00'), c);
  await sinJS(page);
  s = await enviar(page, 'text=Registrar e iniciar factura'); e = await errorDe(page, 'abono');
  c = await shot(page, 'CP04_b_abono_109_99_servidor');
  reg('CP-04', 'Servidor: abono B/. 109.99 sin validación del navegador', 'HTTP 422 y el mismo error', `HTTP ${s}; ${e}`, s === 422 && e.includes('110.00'), c);
  await abrirAlumno(page); await llenarAlumno(page, { ...d4, abono: '110' });
  s = await enviar(page, 'text=Registrar e iniciar factura'); t = await texto(page);
  c = await shot(page, 'CP04_c_abono_110_aceptado');
  reg('CP-04', 'Abono exacto B/. 110.00 (50 %)', 'Se registra; saldo B/. 110.00', `HTTP ${s}; ${(t.match(/Alumno Rosa[^\n]*/) || ['(sin mensaje)'])[0]}`, /Saldo pendiente: B\/\. 110\.00/.test(t), c);

  // ================= CU-04 (Recepcionista) =================
  // CP-05 Pago parcial
  await abrirPago(page); await llenarPago(page, '1', '60', 'Efectivo');
  c = [await shot(page, 'CP05_a_formulario')];
  s = await enviar(page, '#ventana-pago button.boton-azul'); t = await texto(page);
  c.push(await shot(page, 'CP05_b_pago_parcial'));
  reg('CP-05', 'Mariela Vega (debe B/. 110): pago B/. 60 en efectivo', 'Recibo nuevo; "Pago parcial: todavía debe B/. 50.00"; factura Pendiente',
    `HTTP ${s}; ${(t.match(/Pago registrado[^\n]*/) || ['(sin mensaje)'])[0]}`, /todavía debe B\/\. 50\.00/.test(t), c);

  // CP-06 Pago total con transferencia y recibo PDF
  await abrirPago(page); await llenarPago(page, '1', '50', 'Transferencia', 'T-1001');
  s = await enviar(page, '#ventana-pago button.boton-azul'); t = await texto(page);
  c = await shot(page, 'CP06_a_pago_total');
  const rec = (t.match(/REC-(\d+)/) || [])[1];
  const pdf = await pdfTexto(page, '/pagos/recibo/' + rec, 'CP06_b_recibo_REC-' + rec);
  reg('CP-06', 'Mariela Vega: pago B/. 50 por transferencia, ref. T-1001; abrir el recibo', '"La cuenta quedó al día"; el recibo abre como PDF con saldo B/. 0.00',
    `HTTP ${s}; ${(t.match(/Pago registrado[^\n]*/) || [''])[0]}; recibo: HTTP ${pdf.status}, ${pdf.tipo}`, /quedó al día/.test(t) && pdf.inicio === '%PDF', [c, pdf.archivo]);

  // CP-07 Montos fuera de rango
  for (const [m, esperado, nom] of [['0', 'mayor que 0', 'cero'], ['-20', 'mayor que 0', 'negativo'], ['500', 'supera el saldo', 'mayor_saldo']]) {
    await abrirPago(page); await llenarPago(page, '4', m, 'Efectivo');
    await page.click('#ventana-pago button.boton-azul'); const eNav = await errorDe(page, 'monto');
    await sinJS(page); s = await enviar(page, '#ventana-pago button.boton-azul'); e = await errorDe(page, 'monto');
    c = await shot(page, 'CP07_monto_' + nom);
    reg('CP-07', `José Herrera (debe B/. 110): monto ${m}`, `Navegador y servidor rechazan: "${esperado}"; saldo sin cambios`,
      `Navegador: ${eNav} / Servidor HTTP ${s}: ${e}`, eNav.includes(esperado) && s === 422 && e.includes(esperado), c);
  }

  // CP-08 Monto que no es un número
  for (const [m, nom] of [['abc', 'abc'], ['NaN', 'nan']]) {
    await abrirPago(page); await llenarPago(page, '4', m, 'Efectivo');
    await page.click('#ventana-pago button.boton-azul');
    await page.waitForTimeout(800);
    await page.waitForLoadState('networkidle');
    let eNav = '';
    if (page.url().endsWith('/pagos')) eNav = await errorDe(page, 'monto').catch(() => '');
    // si el navegador dejó pasar el formulario, se ve la respuesta del servidor
    t = await texto(page);
    const navegoAlServidor = page.url().endsWith('/pagos/nuevo');
    c = await shot(page, 'CP08_monto_' + nom);
    let observado, ok;
    if (navegoAlServidor) {
      const r500 = t.includes('Ocurrió un error');
      e = r500 ? 'Página de error: "' + t.match(/Ocurrió un error[^\n]*/)[0] + '"' : await errorDe(page, 'monto');
      observado = `Navegador dejó pasar el valor. Servidor: ${e}`;
      ok = !r500 && /número|mayor que 0/.test(e);
    } else {
      await shot(page, 'CP08_monto_' + nom + '_navegador');
      await sinJS(page);
      const [resp] = await Promise.all([page.waitForNavigation(), page.click('#ventana-pago button.boton-azul')]);
      t = await texto(page);
      const r500 = t.includes('Ocurrió un error');
      const eSrv = r500 ? 'página de error 500' : await errorDe(page, 'monto');
      c = [c.replace('.png', '_navegador.png'), await shot(page, 'CP08_monto_' + nom)];
      observado = `Navegador: ${eNav} / Servidor HTTP ${resp.status()}: ${eSrv}`;
      ok = eNav !== '' && resp.status() === 422 && eSrv.includes('Monto no válido');
    }
    reg('CP-08', `José Herrera: monto "${m}" escrito en el formulario`, 'Mensaje "Monto no válido" en el campo; no se registra nada y la app no se cae', observado, ok, c);
  }

  // CP-09 Referencia obligatoria
  await abrirPago(page); await llenarPago(page, '4', '10', 'Tarjeta', '');
  await page.click('#ventana-pago button.boton-azul'); const refNav = await errorDe(page, 'referencia');
  c = [await shot(page, 'CP09_a_referencia_navegador')];
  await sinJS(page); s = await enviar(page, '#ventana-pago button.boton-azul'); e = await errorDe(page, 'referencia');
  c.push(await shot(page, 'CP09_b_referencia_servidor'));
  reg('CP-09', 'José Herrera: B/. 10 con tarjeta sin referencia', 'Navegador y servidor: "La referencia es obligatoria..."', `Navegador: ${refNav} / Servidor HTTP ${s}: ${e}`,
    refNav.includes('obligatoria') && s === 422 && e.includes('obligatoria'), c);

  // ================= CU-03 (Administrador) =================
  await login(page, 'admin', 'Admin2026!');
  const generar = async (id) => {
    await page.goto(URL + '/alumnos');
    const [resp] = await Promise.all([page.waitForNavigation(), page.evaluate((id) => {
      const f = document.createElement('form'); f.method = 'post'; f.action = '/certificados/generar/' + id; document.body.appendChild(f); f.submit();
    }, id)]);
    return resp.status();
  };

  // CP-10 Certificado generado
  await page.goto(URL + '/alumnos'); c = [await shot(page, 'CP10_a_alumnos_admin')];
  const fila = page.locator('tr', { hasText: 'Ana Gómez' });
  const [r10] = await Promise.all([page.waitForNavigation(), fila.locator('text=Generar certificado').click()]);
  t = await texto(page); c.push(await shot(page, 'CP10_b_certificado_generado'));
  const cert = (t.match(/CERT-(\d+)/) || [])[1];
  const pdfc = await pdfTexto(page, `/certificados/${cert}/pdf`, 'CP10_c_certificado_CERT-' + cert);
  c.push(pdfc.archivo);
  reg('CP-10', 'Ana Gómez (Aprobado, 20/16 h, sin deuda): Generar certificado', 'CERT creado con estado «Falta validar»; PDF disponible',
    `HTTP ${r10.status()}; ${(t.match(/Certificado CERT[^\n]*/) || [''])[0]}; PDF: ${pdfc.tipo}`, /Falta validar/.test(t) && pdfc.inicio === '%PDF', c);

  // CP-11 Reglas que impiden generar
  for (const [id, nombre, regla, nom] of [[4, 'José Herrera', 'saldo pendiente', 'saldo'], [2, 'Carlos Espino', 'no está aprobado', 'no_aprobado'],
    [6, 'Iván Castillo', 'No cumple las 36 horas', 'horas'], [3, 'Ana Gómez', 'ya tiene un certificado', 'duplicado']]) {
    await page.goto(URL + '/alumnos');
    const [r] = await Promise.all([page.waitForNavigation(), page.locator('tr', { hasText: nombre }).locator('text=Generar certificado').click()]);
    t = await texto(page); c = await shot(page, 'CP11_rechazo_' + nom);
    const motivos = await page.locator('#ventana-motivos li').allInnerTexts().catch(() => []);
    reg('CP-11', `${nombre}: Generar certificado`, `HTTP 409 y motivo "${regla}"; no se crea certificado`, `HTTP ${r.status()}; ${motivos.join(' | ')}`,
      r.status() === 409 && motivos.join(' ').includes(regla), c);
  }

  // CP-12 Solicitudes no válidas al CU-03
  s = await generar(999); t = await texto(page); c = await shot(page, 'CP12_a_alumno_inexistente');
  reg('CP-12', 'Administrador: generar certificado para el alumno 999 (no existe)', 'Aviso controlado "No se encontró el alumno" (HTTP 404); no se guarda nada',
    `HTTP ${s}; ${(await page.textContent('main')).replace(/\s+/g, ' ').replace('Volver al panel', '').trim()}`, s === 404, c);
  await login(page, 'recepcion', 'Recepcion2026!');
  s = await generar(3); t = await texto(page); c = await shot(page, 'CP12_b_recepcionista_sin_permiso');
  reg('CP-12', 'Recepcionista: intenta generar certificado (escribiendo la dirección)', 'HTTP 403 "Su rol no tiene permiso"', `HTTP ${s}; ${(t.match(/Su rol[^\n]*/) || [''])[0]}`, s === 403, c);

  fs.writeFileSync(path.join(OUT, 'resultados.json'), JSON.stringify({ etiqueta: ETIQ, fecha: new Date().toISOString(), resultados }, null, 2));
  await browser.close();
})().catch((err) => { console.error(err); process.exit(1); });
