#  TECH STACK QUICK REFERENCE
## Rural Rheumatology EHR v3.1

---

##  CURRENT STACK

| Layer | Technology | Version | Notes |
|-------|------------|---------|-------|
| **Frontend** | TypeScript | 5.7+ | Strict mode enabled |
| **UI Framework** | React | 19.x | For complex components |
| **Reactivity** | Alpine.js | 3.x | For simple interactions |
| **Data Fetching** | TanStack Query | 5.x | Caching, real-time |
| **Validation** | Zod | 3.x | Runtime + types |
| **Styling** | Pico CSS + Tailwind | 2.x / 3.x | Semantic + utility |
| **Charts** | ECharts + Chart.js | 5.x / 4.x | Complex + simple |
| **Date Utils** | date-fns | 4.x | Tree-shakeable |
| **Build (Dev)** | Vite | 6.x | Fast HMR |
| **Build (Prod)** | Webpack | 5.x | Code splitting |
| **Backend** | Flask | 3.x | Async-ready |
| **Validation** | Pydantic | 2.x | Type-safe schemas |
| **NLP** | spaCy + scispaCy | 3.7 | Medical NER |
| **Voice** | Vosk | 0.3 | Offline STT |

---

##  QUICK COMMANDS

```bash
# Development
npm run dev          # Start Vite dev server (port 5173)
python backend/app.py # Start Flask backend (port 8000)

# Production Build
npm run build        # Sass + Webpack bundle

# Type Checking
npx tsc --noEmit     # Check TypeScript errors
```

---

##  PROJECT STRUCTURE

```
frontend/src/
 components/      # React components (.tsx)
 modules/         # Alpine.js logic (.ts)
 types/           # TypeScript declarations
 queries.ts       # TanStack Query hooks
 schemas.ts       # Zod validation schemas
 index.tsx        # Entry point

backend/
 routes/          # Flask blueprints
 services/        # NLP engine
 templates/       # Jinja2 HTML
 static/dist/     # Webpack output
 schemas.py       # Pydantic models
```

---

##  KEY CONFIGURATIONS

### TypeScript (tsconfig.json)
- Target: ES2020
- JSX: react-jsx
- Strict mode enabled
- Module resolution: node

### Webpack (webpack.config.js)
- Entry: frontend/src/index.tsx
- Output: backend/static/dist/
- Loaders: ts-loader only
- Code splitting: vendors chunk

### Tailwind (tailwind.config.js)
- Content: templates + frontend/src
- Works alongside Pico CSS

---

**Last Updated:** December 2024
