import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { copyFileSync, cpSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss(), {
    name: 'bundle-privacy-policy',
    closeBundle() {
      copyFileSync('privacy.html', 'dist/privacy.html');
      // Preserve the full calendar, regional languages and existing artwork offline in the app bundle.
      if (process.env.VITE_MOBILE_BUILD === 'true') {
        for (const file of readdirSync('.')) {
          if (/\.(js|css)$/.test(file) && file !== 'sw.js') copyFileSync(file, `dist/${file}`);
        }
        cpSync('assets', 'dist/assets', { recursive: true });
        copyFileSync('manifest.webmanifest', 'dist/manifest.webmanifest');
        copyFileSync('dist/index.html', 'dist/app.html');
        const shell = readFileSync('app-shell.js', 'utf8').replace('\"/app\"', '\"/app.html\"').replace('if (\"serviceWorker\" in navigator)', 'if (false)');
        writeFileSync('dist/app-shell.js', shell);
        const origin = JSON.stringify(process.env.VITE_API_BASE_URL);
        const bootstrap = `<script>const nativeFetch = window.fetch.bind(window); window.fetch = (input, init) => { if (typeof input === 'string' && input.startsWith('/api/')) input = ${origin} + input; return nativeFetch(input, init); };</script>`;
        const extras = '<link rel="stylesheet" href="/regional-ui.css"><link rel="stylesheet" href="/app-shell.css">' +
          ['share-card', 'live-activity', 'classic-extras', 'regional-ui', 'app-shell', 'launch-enhancements']
            .map(name => `<script defer src="/${name}.js"></script>`).join('');
        const html = readFileSync('classic.html', 'utf8')
          .replace('<head>', `<head>${bootstrap}`)
          .replace('</head>', `${extras}</head>`)
          .replace('</body>', '<p style="text-align:center;padding-bottom:90px"><a href="/privacy.html">Privacy policy</a></p></body>');
        writeFileSync('dist/classic.html', html);
        writeFileSync('dist/index.html', html);
      }
    },
  }],
  build: {
    outDir: 'dist',
    assetsDir: '_app',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8088',
      '/assets': 'http://localhost:8088',
    },
  },
});
