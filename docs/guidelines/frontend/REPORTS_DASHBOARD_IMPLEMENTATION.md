# Reports & Dashboard Implementation Guidelines

**Status:** Rural Rheumatology EHR | Production-Ready | IE11 Compatible
**Charting Library:** ECharts 5.5.0 (87KB minified) ✅
**Target:** 2GB Old PC Performance | Pentium 4 Compatible

---

## 1. Architecture Overview

### Tech Stack
*   **Frontend**:
    *   Alpine.js (State management)
    *   HTMX (Async data loading)
    *   ECharts 5.5.0 (Charting - Lazy loaded)
    *   Vanilla CSS (Pico.css base)
*   **Backend**:
    *   Flask (REST API)
    *   SQLite (Database)
    *   Jinja2 (Template rendering)

### Performance Guarantees
*   **Initial Load**: <2 seconds on Pentium 4 / 2GB RAM.
*   **Chart Render**: 300-500ms.
*   **Bundle Size**: Keep total page load <150KB.

---

## 2. Dashboard Implementation

### Layout
*   **Header**: Quick Stats (KPIs) - Patients Today, Avg DAS28, Remission %, Pending Reviews.
*   **Charts**: Lazy-loaded ECharts (Disease Distribution Pie, DAS28 Trend Line).
*   **Table**: Recent Visits (HTMX loaded).

### API Endpoints (`/api/dashboard/*`)
*   `GET /stats`: Returns JSON with KPI data.
*   `GET /distribution`: Returns JSON for Pie Chart.
*   `GET /trend`: Returns JSON for Line Chart.
*   `GET /recent-visits`: Returns HTML fragment for the table.

---

## 3. Reports Implementation

### Layout
*   **Builder**: Form to select Report Type, Date Range, Patient.
*   **Preview**: Dynamic HTML preview of the report.
*   **Export**: Print (Native), PDF (Server-side), CSV.

### API Endpoints (`/api/reports/*`)
*   `POST /generate`: Generates report data/preview.
*   `GET /preview`: Returns HTML fragment for report preview.
*   `GET /export-pdf`: Returns PDF file.
*   `GET /export-csv`: Returns CSV file.

---

## 4. ECharts Integration Strategy

### Lazy Loading
Do NOT load ECharts in `<head>`. Load it on demand when a chart is requested or after the main content has painted.

```javascript
async function loadECharts() {
    if (typeof echarts === 'undefined') {
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = '/static/js/libs/echarts.min.js'; // Local file
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }
}
```

### Offline Support
*   Download `echarts.min.js` and place it in `backend/static/js/libs/`.
*   Ensure all CSS/JS assets are local.

---

## 5. Implementation Steps
1.  **Backend**: Create `backend/routes/analytics.py` and register blueprint.
2.  **Frontend**:
    *   Update `dashboard.html` with Alpine.js and HTMX.
    *   Update `reports.html` with Report Builder form.
    *   Create `dashboard_logic.js` and `reports_logic.js`.
3.  **Assets**: Add `echarts.min.js`.
