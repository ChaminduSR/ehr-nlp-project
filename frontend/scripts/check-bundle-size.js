const fs = require('fs')
const path = require('path')

// thresholds
const GZIP_LIMIT = 150 * 1024 // bytes
const BROTLI_LIMIT = 120 * 1024 // bytes

const distDir = path.resolve(__dirname, '..', 'dist')
const manifestPathCandidates = [
  path.join(distDir, 'manifest.json'),
  path.join(distDir, '.vite', 'manifest.json')
]
let manifestPath = null
for (const p of manifestPathCandidates) if (fs.existsSync(p)) { manifestPath = p; break }

if (!fs.existsSync(distDir)) {
  console.error('dist directory not found. Run `npm run build` in frontend first.')
  process.exit(2)
}

if (!manifestPath) {
  console.error('manifest.json not found in dist (checked dist/manifest.json and dist/.vite/manifest.json). Ensure build.manifest=true in Vite config.')
  process.exit(2)
}

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'))
let entry = null
for (const key of Object.keys(manifest)) {
  if (manifest[key].isEntry) { entry = manifest[key]; break }
}

if (!entry) {
  console.error('No entry found in manifest.json')
  process.exit(2)
}

const file = entry.file // e.g. assets/index.xxxxx.js
const filePath = path.join(distDir, file)
const brPath = filePath + '.br'
const gzPath = filePath + '.gz'

function sizeOf(p) {
  if (!fs.existsSync(p)) return null
  return fs.statSync(p).size
}

const brSize = sizeOf(brPath)
const gzSize = sizeOf(gzPath)

console.log('Initial entry file:', file)
console.log('Brotli size:', brSize !== null ? (brSize / 1024).toFixed(1) + ' KB' : 'missing')
console.log('Gzip size:', gzSize !== null ? (gzSize / 1024).toFixed(1) + ' KB' : 'missing')

let failed = false
if (brSize === null) {
  console.warn('Brotli file missing; ensure compression plugin ran')
} else if (brSize > BROTLI_LIMIT) {
  console.error(`Brotli size ${brSize} bytes exceeds limit ${BROTLI_LIMIT} bytes`)
  failed = true
}

if (gzSize === null) {
  console.warn('Gzip file missing; ensure compression plugin ran')
} else if (gzSize > GZIP_LIMIT) {
  console.error(`Gzip size ${gzSize} bytes exceeds limit ${GZIP_LIMIT} bytes`)
  failed = true
}

if (failed) process.exit(3)
console.log('Bundle size checks passed')
process.exit(0)
