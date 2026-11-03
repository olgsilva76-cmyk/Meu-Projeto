// Renderiza animacao.html quadro a quadro (30 fps) e gera o vídeo com ffmpeg.
// Uso: node renderizar.js [saida.mp4] [--preview SEGUNDOS...]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const FPS = 30;
const args = process.argv.slice(2);
const previewIdx = args.indexOf('--preview');
const preview = previewIdx >= 0 ? args.slice(previewIdx + 1).map(Number) : null;
const out = (previewIdx === 0 ? null : args[0]) || path.join(__dirname, 'video_sem_audio.mp4');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'animacao.html'));
  await page.evaluate(() => document.fonts.ready);
  const duration = await page.evaluate(() => window.DURATION);

  if (preview) {
    for (const t of preview) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(process.env.PREVIEW_DIR || __dirname, `preview_${t.toFixed(2)}.png`) });
    }
    await browser.close();
    return;
  }

  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'medium', out], { stdio: ['pipe', 'inherit', 'inherit'] });

  const total = Math.round(duration * FPS);
  for (let f = 0; f < total; f++) {
    await page.evaluate(t => window.render(t), f / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) process.stdout.write(`quadro ${f}/${total}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('ok ->', out);
})();
