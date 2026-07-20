const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Set viewport to 16:9 landscape (presentation aspect ratio)
  await page.setViewport({ width: 1920, height: 1080 });

  // Load the presentation HTML file
  const filePath = path.resolve(__dirname, 'presentation.html');
  await page.goto(`file://${filePath}`, { waitUntil: 'networkidle0', timeout: 30000 });

  // CRITICAL: Force 'screen' media so the dark theme is preserved (not print white)
  await page.emulateMediaType('screen');

  // Make ALL slides visible (they start hidden due to scroll-reveal)
  await page.evaluate(() => {
    document.querySelectorAll('.slide').forEach(s => {
      s.style.opacity = '1';
      s.style.transform = 'none';
    });
  });

  // Generate the PDF with each slide as a separate landscape page
  await page.pdf({
    path: path.resolve(__dirname, 'presentation.pdf'),
    width: '1920px',
    height: '1080px',
    printBackground: true,          // Keep dark background, colors, gradients
    preferCSSPageSize: false,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });

  console.log('✅ presentation.pdf oluşturuldu!');
  await browser.close();
})();
