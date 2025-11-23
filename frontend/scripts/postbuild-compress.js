const fs = require('fs')
const path = require('path')
const zlib = require('zlib')

const distDir = path.resolve(__dirname, '..', 'dist')

function compressFile(filePath) {
  const buf = fs.readFileSync(filePath)
  // gzip
  const gz = zlib.gzipSync(buf, { level: zlib.constants.Z_BEST_COMPRESSION })
  fs.writeFileSync(filePath + '.gz', gz)
  // brotli
  if (zlib.brotliCompressSync) {
    const br = zlib.brotliCompressSync(buf, { params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 11 } })
    fs.writeFileSync(filePath + '.br', br)
  }
}

function walkAndCompress(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  for (const e of entries) {
    const full = path.join(dir, e.name)
    if (e.isDirectory()) {
      walkAndCompress(full)
    } else if (e.isFile()) {
      if (full.endsWith('.js') || full.endsWith('.css') || full.endsWith('.html') || full.endsWith('.svg')) {
        try {
          compressFile(full)
          console.log('Compressed', full)
        } catch (err) {
          console.error('Failed to compress', full, err)
        }
      }
    }
  }
}

if (!fs.existsSync(distDir)) {
  console.error('dist directory not found; run build first')
  process.exit(1)
}

walkAndCompress(distDir)
console.log('Post-build compression complete')
