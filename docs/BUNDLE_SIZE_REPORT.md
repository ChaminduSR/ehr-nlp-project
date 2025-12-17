# Bundle Size Report

**Last Updated**: December 2024
**Target Budget**: 150 KB (gzipped)
**Planning Budget**: 500 KB (uncompressed)

---

## Current Bundle Analysis

### CSS Assets

| File | Uncompressed | Gzipped | Description |
|------|--------------|---------|-------------|
| `theme.css` | 72 KB | ~12 KB | Pico.css + custom theme + extracted components |
| `custom.css` | 1.1 KB | ~0.4 KB | Legacy utilities |
| **CSS Total** | **73 KB** | **~12 KB** | |

### JavaScript Assets

| File | Uncompressed | Gzipped | Description |
|------|--------------|---------|-------------|
| `vendors.bundle.js` | 102 KB | 33 KB | Alpine.js, HTMX, date-fns |
| `main.bundle.js` | 23 KB | 8 KB | Application code |
| `350.chunk.js` | 177 KB | 52 KB | Konva.js (lazy-loaded) |
| `joint-diagram.chunk.js` | 4 KB | 1.5 KB | Joint diagram logic |
| **JS Total** | **306 KB** | **~95 KB** | |

### Total Bundle

| Metric | Value |
|--------|-------|
| **Total Uncompressed** | 379 KB |
| **Total Gzipped** | ~107 KB |
| **Budget Used** | 71% of 150 KB |
| **Remaining Headroom** | 43 KB |

---

## Budget Visualization

```
Target (150 KB gzipped):
[██████████████░░░░░░] 71% used (107 KB / 150 KB)

Planning Budget (500 KB uncompressed):
[███████████████░░░░░] 76% used (379 KB / 500 KB)

Status: ✅ WITHIN BUDGET
```

---

## Bundle Composition

### CSS Breakdown (~72 KB)

| Component | Size | Source |
|-----------|------|--------|
| Pico.css (tree-shaken) | ~55 KB | @picocss/pico |
| Custom healthcare theme | ~9 KB | custom-theme.scss |
| Extracted components | ~8 KB | _extracted-components.scss |

**Tree-shaken Pico modules** (disabled to save ~12 KB):
- `content/code`, `content/figure`
- `forms/input-color`, `forms/input-date`, `forms/input-file`, `forms/input-search`
- `components/accordion`, `components/dropdown`, `components/loading`, `components/progress`, `components/tooltip`

### JS Breakdown (~306 KB)

| Library | Size | Loading |
|---------|------|---------|
| Alpine.js | ~15 KB | Immediate |
| HTMX | ~14 KB | Immediate |
| date-fns | ~8 KB | Immediate |
| Konva.js | ~177 KB | **Lazy-loaded** |
| Application code | ~27 KB | Immediate |

---

## Recent Changes

### December 2024 - Modern Theme Components

Added 8 UI components extracted from DaisyUI/FloatUI/FlyonUI:

| Component | Size | Impact |
|-----------|------|--------|
| Stats/KPI | 1.2 KB | Dashboard metrics |
| Glass Card | 0.8 KB | Modern card effect |
| Toast Notifications | 1.0 KB | Save status alerts |
| Modern Badges | 0.6 KB | DAS28 severity |
| Skeleton Loaders | 0.5 KB | Loading states |
| Button Variants | 0.9 KB | Ghost/outline styles |
| Tabs | 0.8 KB | Tab navigation |
| Timeline | 1.0 KB | Visit history |
| **Total Addition** | **~7 KB** | +0 KB gzipped |

**Strategy**: Component extraction (pure CSS) instead of plugin installation
**Benefit**: No runtime overhead, precise control, minimal footprint

---

## Optimization Strategies Applied

### 1. Pico.css Tree-Shaking
- Disabled unused modules via SCSS `$modules` config
- Savings: ~12 KB

### 2. Lazy Loading
- Konva.js loaded only when joint diagram is needed
- ECharts loaded only when charts are requested

### 3. Code Splitting (Webpack)
- Vendor bundle separated from application code
- Joint diagram logic in separate chunk

### 4. Component Extraction
- Copied specific CSS from UI libraries instead of installing plugins
- No Tailwind/DaisyUI plugin overhead

### 5. No Web Fonts
- System font stack only
- Savings: ~50-100 KB

---

## Future Optimization Opportunities

| Optimization | Potential Savings | Complexity |
|--------------|-------------------|------------|
| Remove unused date-fns functions | ~3-5 KB | Low |
| Further Pico.css tree-shaking | ~2-3 KB | Low |
| Compress Konva.js more aggressively | ~10 KB | Medium |
| Replace ECharts with lightweight alternative | ~50 KB | High |

---

## Build Commands

```powershell
# Build CSS (production, compressed)
npm run sass:build

# Build JS (production, minified)
npm run build:js

# Full production build
npm run build

# Analyze bundle (opens visualization)
npm run analyze
```

---

## Monitoring Bundle Size

After making changes, verify bundle sizes:

```powershell
# Check CSS size
ls backend/static/css/theme.css

# Check JS sizes
ls backend/static/dist/*.js

# Check gzipped size
gzip -c backend/static/css/theme.css | wc -c
```

---

## Related Documentation

- [Modern Theme Components](guidelines/frontend/MODERN_THEME_COMPONENTS.md) - Component reference
- [Design Specifications](guidelines/frontend/DESIGN_SPECIFICATIONS.md) - Design system
- [Tech Stack Quick Start](Tech-Stack-Quick-Start.md) - Development setup
