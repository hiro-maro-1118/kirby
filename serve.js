const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3001;
const MIME_TYPES = {
  '.html': 'text/html; charset=UTF-8',
  '.js': 'text/javascript; charset=UTF-8',
  '.css': 'text/css; charset=UTF-8',
  '.json': 'application/json; charset=UTF-8',
  '.webp': 'image/webp',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
  let reqUrl = req.url.split('?')[0];
  let filePath = path.join(__dirname, reqUrl === '/' ? 'index.html' : reqUrl);

  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain; charset=UTF-8' });
        res.end('404 Not Found');
      } else {
        res.writeHead(500);
        res.end(`Server Error: ${err.code}`);
      }
    } else {
      // JSONはキャッシュを無効化
      const headers = { 'Content-Type': contentType };
      if (ext === '.json') {
        headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
      }
      res.writeHead(200, headers);
      res.end(content, 'utf-8');
    }
  });
});

function startServer(port) {
  server.listen(port, () => {
    console.log(`\n⭐ ぷぷぷ育成フレンズ サーバーが起動しました！`);
    console.log(`👉 http://localhost:${port}\n`);
  }).on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.log(`⚠️ ポート ${port} は使用中のため、ポート ${port + 1} で試行します...`);
      startServer(port + 1);
    } else {
      console.error(err);
    }
  });
}

startServer(PORT);
