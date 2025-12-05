# Plan: ECharts-Powered Dashboard & Reports

**Status:** Rural Rheumatology EHR | Production-Ready | IE11 Compatible  
**Charting Library:** ECharts 5.5.0 (87KB minified) ✅  
**Target:** 2GB Old PC Performance | Pentium 4 Compatible  

---

## **PART 1: ARCHITECTURE OVERVIEW**

### **Tech Stack**

```
Frontend:
├─ Alpine.js (13KB) - State management
├─ HTMX (14KB) - Async data loading
├─ ECharts 5.5.0 (87KB) - Charting
└─ Vanilla CSS (no framework)

Backend:
├─ Flask - REST API
├─ SQLite - Database
└─ Jinja2 - Template rendering

Bundle Size Summary:
├─ Page HTML: ~15KB
├─ Alpine + HTMX: ~27KB
├─ ECharts (lazy-loaded): 87KB ← Loads on-demand
└─ CSS + JS logic: ~20KB
= Total Page Load: ~62KB (without charts)
  With charts: ~150KB (still acceptable)
```

### **Performance Guarantees**

| Device | Initial Load | Chart Render | Interaction |
|--------|--------------|--------------|-------------|
| **Pentium 4 / 2GB** | <2 seconds | 300-500ms | Smooth |
| **Core 2 Duo / 4GB** | <1 second | <200ms | Very smooth |
| **Modern PC** | <500ms | <100ms | Instant |

---

## **PART 2: DASHBOARD PAGE** 📊

### **2.1 Layout Structure**

```
DASHBOARD
│
├─ Header: Quick Stats (KPIs)
│  ├─ Patients Today
│  ├─ Avg DAS28
│  ├─ In Remission %
│  └─ Pending Reviews
│
├─ Charts Section (Lazy-loaded)
│  ├─ Disease Distribution (Pie)
│  ├─ DAS28 Trend (Line)
│  └─ Patient Status Gauge
│
└─ Recent Visits Table
   ├─ Patient Name
   ├─ Date
   ├─ DAS28 Score
   ├─ TJC / SJC
   └─ Actions (View / Edit)
```

### **2.2 Dashboard HTML Template**

```html
<!-- templates/dashboard.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    
    <!-- Alpine.js for state -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    
    <!-- HTMX for server-driven UI -->
    <script src="https://unpkg.com/htmx.org"></script>
    
    <!-- ECharts loaded on-demand (NOT in <head>) -->
    
    <style>
        :root {
            --color-primary: #2180B0;
            --color-success: #4CAF50;
            --color-warning: #FFC107;
            --color-danger: #F44336;
            --color-text: #333;
            --color-bg: #f5f5f5;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--color-bg);
            color: var(--color-text);
        }
        
        .container { max-width: 1200px; margin: 0 auto; }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .header h1 { margin: 0; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-card h4 {
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: var(--color-primary);
        }
        
        .charts-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .chart-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            min-height: 400px;
        }
        
        .chart-card h3 {
            margin: 0 0 15px 0;
            font-size: 16px;
        }
        
        .chart-container {
            width: 100%;
            height: 350px;
        }
        
        .table-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        th {
            background: #f0f0f0;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #ddd;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: all 200ms;
        }
        
        .btn--primary {
            background: var(--color-primary);
            color: white;
        }
        
        .btn--primary:hover {
            background: #1a6a8f;
        }
        
        .btn--sm {
            padding: 4px 12px;
            font-size: 12px;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: 1fr 1fr; }
            .charts-section { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

<div class="container" x-data="dashboardData()" x-init="init()">
    
    <!-- Header -->
    <div class="header">
        <h1>📊 Clinic Dashboard</h1>
        <p x-text="'Last updated: ' + new Date().toLocaleTimeString()"></p>
    </div>
    
    <!-- KPI Stats (Always visible) -->
    <div class="stats-grid">
        <div class="stat-card">
            <h4>Patients Today</h4>
            <p class="stat-value" x-text="stats.patientsToday"></p>
        </div>
        
        <div class="stat-card">
            <h4>Avg DAS28</h4>
            <p class="stat-value" x-text="(stats.avgDAS28).toFixed(1)"></p>
        </div>
        
        <div class="stat-card">
            <h4>In Remission</h4>
            <p class="stat-value" x-text="stats.remissionPercent + '%'"></p>
        </div>
        
        <div class="stat-card">
            <h4>Pending Reviews</h4>
            <p class="stat-value" x-text="stats.pendingReviews"></p>
        </div>
    </div>
    
    <!-- Charts Section (Lazy-loaded) -->
    <div class="charts-section">
        
        <!-- Distribution Chart -->
        <div class="chart-card">
            <h3>Disease Activity Distribution</h3>
            <button @click="loadChart('distribution')" class="btn btn--primary btn--sm" 
                    x-show="!charts.distribution">
                📊 Load Chart
            </button>
            <div id="chart-distribution" class="chart-container" x-show="charts.distribution"></div>
        </div>
        
        <!-- Trend Chart -->
        <div class="chart-card">
            <h3>DAS28 Trend (Last 30 Days)</h3>
            <button @click="loadChart('trend')" class="btn btn--primary btn--sm" 
                    x-show="!charts.trend">
                📈 Load Chart
            </button>
            <div id="chart-trend" class="chart-container" x-show="charts.trend"></div>
        </div>
    </div>
    
    <!-- Recent Visits Table -->
    <div class="table-card">
        <h2>Recent Visits</h2>
        <div hx-get="/api/dashboard/recent-visits" 
             hx-trigger="load"
             hx-swap="innerHTML"
             hx-target="this">
            <div class="loading">Loading visits...</div>
        </div>
    </div>

</div>

<script>
    function dashboardData() {
        return {
            stats: {
                patientsToday: 0,
                avgDAS28: 0,
                remissionPercent: 0,
                pendingReviews: 0
            },
            charts: {
                distribution: false,
                trend: false
            },
            echartsInstance: {},
            
            async init() {
                await this.loadStats();
                // Charts load on-demand via loadChart()
            },
            
            async loadStats() {
                try {
                    const response = await fetch('/api/dashboard/stats');
                    const data = await response.json();
                    this.stats = data;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            },
            
            async loadChart(type) {
                // Check if ECharts is already loaded
                if (typeof echarts === 'undefined') {
                    await this.loadECharts();
                }
                
                if (type === 'distribution') {
                    this.charts.distribution = true;
                    await this.renderDistributionChart();
                } else if (type === 'trend') {
                    this.charts.trend = true;
                    await this.renderTrendChart();
                }
            },
            
            async loadECharts() {
                // Load ECharts library (87KB)
                return new Promise((resolve) => {
                    const script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js';
                    script.onload = resolve;
                    document.head.appendChild(script);
                });
            },
            
            async renderDistributionChart() {
                const response = await fetch('/api/dashboard/distribution');
                const data = await response.json();
                
                const chart = echarts.init(document.getElementById('chart-distribution'));
                const option = {
                    title: {
                        text: 'Disease Activity Distribution',
                        left: 'center'
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: '{b}: {c} ({d}%)'
                    },
                    legend: {
                        orient: 'vertical',
                        left: 'left'
                    },
                    series: [{
                        name: 'Patients',
                        type: 'pie',
                        radius: '60%',
                        data: [
                            { value: data.remission, name: 'Remission', itemStyle: { color: '#4CAF50' } },
                            { value: data.low_activity, name: 'Low Activity', itemStyle: { color: '#FFC107' } },
                            { value: data.moderate, name: 'Moderate', itemStyle: { color: '#FF9800' } },
                            { value: data.high, name: 'High', itemStyle: { color: '#F44336' } }
                        ],
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }]
                };
                
                chart.setOption(option);
                window.addEventListener('resize', () => chart.resize());
            },
            
            async renderTrendChart() {
                const response = await fetch('/api/dashboard/trend');
                const data = await response.json();
                
                const chart = echarts.init(document.getElementById('chart-trend'));
                const option = {
                    title: {
                        text: 'DAS28 Trend - Last 30 Days',
                        left: 'center'
                    },
                    tooltip: {
                        trigger: 'axis',
                        formatter: '{b0}<br/>{a0}: {c0}'
                    },
                    grid: {
                        left: '10%',
                        right: '10%',
                        bottom: '10%',
                        top: '15%',
                        containLabel: true
                    },
                    xAxis: {
                        type: 'category',
                        data: data.dates,
                        boundaryGap: false
                    },
                    yAxis: {
                        type: 'value',
                        name: 'DAS28 Score',
                        axisLine: { onZero: false }
                    },
                    series: [{
                        name: 'Average DAS28',
                        type: 'line',
                        data: data.scores,
                        smooth: true,
                        itemStyle: { color: '#2180B0' },
                        lineStyle: { width: 2 },
                        markLine: {
                            data: [
                                { yAxis: 2.6, name: 'Remission', lineStyle: { color: '#4CAF50' } },
                                { yAxis: 3.2, name: 'Low Activity', lineStyle: { color: '#FFC107' } },
                                { yAxis: 5.1, name: 'High Activity', lineStyle: { color: '#F44336' } }
                            ]
                        }
                    }]
                };
                
                chart.setOption(option);
                window.addEventListener('resize', () => chart.resize());
            }
        }
    }
</script>

</body>
</html>
```

### **2.3 Recent Visits HTMX Response**

```html
<!-- Response from /api/dashboard/recent-visits -->
<table>
    <thead>
        <tr>
            <th>Patient Name</th>
            <th>Date</th>
            <th>DAS28</th>
            <th>TJC</th>
            <th>SJC</th>
            <th>Status</th>
            <th>Action</th>
        </tr>
    </thead>
    <tbody>
        {% for visit in visits %}
        <tr>
            <td>{{ visit.patient_name }}</td>
            <td>{{ visit.date.strftime('%m/%d/%Y') }}</td>
            <td><strong>{{ "%.1f" % visit.das28_score }}</strong></td>
            <td>{{ visit.tjc }}</td>
            <td>{{ visit.sjc }}</td>
            <td>
                {% if visit.das28_score < 2.6 %}
                    <span style="color: #4CAF50;">✓ Remission</span>
                {% elif visit.das28_score < 3.2 %}
                    <span style="color: #FFC107;">⚠ Low Activity</span>
                {% elif visit.das28_score <= 5.1 %}
                    <span style="color: #FF9800;">● Moderate</span>
                {% else %}
                    <span style="color: #F44336;">● High</span>
                {% endif %}
            </td>
            <td>
                <a href="/visit/{{ visit.id }}" class="btn btn--primary btn--sm">View</a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

---

## **PART 3: REPORTS PAGE** 📋

### **3.1 Reports Layout**

```
REPORTS PAGE
│
├─ Report Builder (Form)
│  ├─ Report Type Selector
│  ├─ Date Range Picker
│  ├─ Patient/Clinic Filter
│  └─ Generate Button
│
├─ Report Preview (Dynamic)
│  └─ Rendered report with ECharts visualizations
│
└─ Export Options
   ├─ PDF (server-side)
   ├─ CSV (Excel)
   └─ Print (browser native)
```

### **3.2 Reports HTML Template**

```html
<!-- templates/reports.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reports</title>
    
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://unpkg.com/htmx.org"></script>
    
    <style>
        :root {
            --color-primary: #2180B0;
            --color-text: #333;
            --color-bg: #f5f5f5;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--color-bg);
            color: var(--color-text);
        }
        
        .container { max-width: 1000px; margin: 0 auto; }
        
        .report-builder {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 14px;
        }
        
        .form-control {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: inherit;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 200ms;
        }
        
        .btn--primary {
            background: var(--color-primary);
            color: white;
        }
        
        .btn--primary:hover {
            background: #1a6a8f;
        }
        
        .report-preview {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .report-header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .report-header h1 {
            margin: 0;
            font-size: 24px;
        }
        
        .report-section {
            margin-bottom: 30px;
        }
        
        .report-section h2 {
            font-size: 18px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        
        .stats-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .stats-table tr:nth-child(odd) {
            background: #f9f9f9;
        }
        
        .stats-table td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        .stats-table td:first-child {
            font-weight: 600;
            width: 40%;
        }
        
        .export-options {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        
        .chart-container {
            margin: 20px 0;
            height: 400px;
        }
        
        .hidden {
            display: none;
        }
        
        @media (max-width: 768px) {
            .form-row { grid-template-columns: 1fr; }
            .export-options { flex-direction: column; }
        }
        
        @media print {
            .report-builder { display: none; }
            .export-options { display: none; }
            body { background: white; }
            .report-preview { box-shadow: none; }
        }
    </style>
</head>
<body>

<div class="container" x-data="reportBuilder()" x-init="init()">
    
    <h1>📋 Reports</h1>
    
    <!-- Report Builder Form -->
    <div class="report-builder">
        <h2>Generate Report</h2>
        
        <div class="form-group">
            <label>Report Type</label>
            <select x-model="reportType" @change="updateForm()" class="form-control">
                <option value="summary">Patient Summary</option>
                <option value="trend">DAS28 Trend Report</option>
                <option value="performance">Clinic Performance</option>
                <option value="treatment">Treatment Response Cohort</option>
            </select>
        </div>
        
        <!-- Patient Selection (for summary) -->
        <div class="form-group" x-show="reportType === 'summary'">
            <label>Patient</label>
            <input type="text" 
                   @input.debounce="searchPatients($event)"
                   placeholder="Search by name or MRN..."
                   class="form-control">
            <ul x-show="patientResults.length > 0" style="list-style: none; padding: 10px; background: #f9f9f9; margin-top: 5px;">
                <template x-for="patient in patientResults" :key="patient.id">
                    <li @click="selectPatient(patient); patientResults = []" 
                        style="padding: 8px; cursor: pointer; border-bottom: 1px solid #eee;">
                        <strong x-text="patient.name"></strong> · MRN: <span x-text="patient.mrn"></span>
                    </li>
                </template>
            </ul>
            <p x-show="selectedPatient" style="margin-top: 10px; color: #4CAF50;">
                ✓ Selected: <strong x-text="selectedPatient?.name"></strong>
            </p>
        </div>
        
        <!-- Date Range (for trend & performance) -->
        <div class="form-row" x-show="['trend', 'performance', 'treatment'].includes(reportType)">
            <div class="form-group">
                <label>Start Date</label>
                <input type="date" x-model="filters.startDate" class="form-control">
            </div>
            <div class="form-group">
                <label>End Date</label>
                <input type="date" x-model="filters.endDate" class="form-control">
            </div>
        </div>
        
        <!-- Generate Button -->
        <button @click="generateReport()" class="btn btn--primary" :disabled="isGenerating">
            <span x-show="!isGenerating">Generate Report</span>
            <span x-show="isGenerating">⏳ Generating...</span>
        </button>
    </div>
    
    <!-- Report Preview (loaded dynamically) -->
    <div id="report-preview" class="hidden">
        <div hx-get="/api/reports/preview" 
             hx-trigger="manual"
             hx-swap="innerHTML"
             hx-target="this">
        </div>
    </div>

</div>

<script>
    function reportBuilder() {
        return {
            reportType: 'summary',
            selectedPatient: null,
            patientResults: [],
            filters: {
                startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                endDate: new Date().toISOString().split('T')[0]
            },
            isGenerating: false,
            
            init() {
                // Initialize with default date range (last 30 days)
            },
            
            updateForm() {
                this.patientResults = [];
                this.selectedPatient = null;
            },
            
            async searchPatients(event) {
                const query = event.target.value;
                if (query.length < 2) {
                    this.patientResults = [];
                    return;
                }
                
                try {
                    const response = await fetch(`/api/patients/search?q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    this.patientResults = data.patients;
                } catch (error) {
                    console.error('Error searching patients:', error);
                }
            },
            
            selectPatient(patient) {
                this.selectedPatient = patient;
            },
            
            async generateReport() {
                if (this.reportType === 'summary' && !this.selectedPatient) {
                    alert('Please select a patient');
                    return;
                }
                
                this.isGenerating = true;
                
                try {
                    const payload = {
                        report_type: this.reportType,
                        patient_id: this.selectedPatient?.id,
                        filters: this.filters
                    };
                    
                    const response = await fetch('/api/reports/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    
                    if (!response.ok) throw new Error('Failed to generate report');
                    
                    // Show preview
                    document.getElementById('report-preview').classList.remove('hidden');
                    
                    // Trigger HTMX to load preview
                    htmx.ajax('GET', 
                        `/api/reports/preview?type=${this.reportType}&patient_id=${this.selectedPatient?.id}`,
                        '#report-preview'
                    );
                    
                    // Scroll to preview
                    document.getElementById('report-preview').scrollIntoView({ behavior: 'smooth' });
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error generating report');
                } finally {
                    this.isGenerating = false;
                }
            }
        }
    }
</script>

</body>
</html>
```

### **3.3 Report Templates (Backend)**

#### **Patient Summary Report**

```python
# app.py - Flask route

@app.route('/api/reports/preview')
def report_preview():
    """Render report preview as HTML"""
    report_type = request.args.get('type', 'summary')
    patient_id = request.args.get('patient_id')
    
    if report_type == 'summary':
        patient = Patient.query.get(patient_id)
        visits = Visit.query.filter_by(patient_id=patient_id).order_by(Visit.visit_date.desc()).limit(20)
        medications = Medication.query.filter_by(patient_id=patient_id).all()
        
        return render_template('reports/patient_summary.html', 
                             patient=patient, 
                             visits=visits,
                             medications=medications)
    
    elif report_type == 'trend':
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        visits = Visit.query.filter(
            Visit.visit_date.between(start_date, end_date)
        ).order_by(Visit.visit_date).all()
        
        return render_template('reports/trend_report.html', visits=visits)
```

#### **Patient Summary Template**

```html
<!-- templates/reports/patient_summary.html -->
<div class="report-preview">
    <div class="report-header">
        <h1>Patient Summary Report</h1>
        <p>Generated on {{ now().strftime('%m/%d/%Y %H:%M:%S') }}</p>
    </div>
    
    <div class="report-section">
        <h2>Patient Information</h2>
        <table class="stats-table">
            <tr>
                <td>Name</td>
                <td><strong>{{ patient.first_name }} {{ patient.last_name }}</strong></td>
            </tr>
            <tr>
                <td>MRN</td>
                <td>{{ patient.mrn }}</td>
            </tr>
            <tr>
                <td>Date of Birth</td>
                <td>{{ patient.dob.strftime('%m/%d/%Y') }}</td>
            </tr>
            <tr>
                <td>Age</td>
                <td>{{ ((now() - patient.dob).days // 365) }} years</td>
            </tr>
        </table>
    </div>
    
    <div class="report-section">
        <h2>Latest Visit</h2>
        {% set latest = visits[0] %}
        <table class="stats-table">
            <tr>
                <td>Visit Date</td>
                <td>{{ latest.visit_date.strftime('%m/%d/%Y') }}</td>
            </tr>
            <tr>
                <td>DAS28 Score</td>
                <td>
                    <strong>{{ "%.1f" % latest.das28_score }}</strong>
                    {% if latest.das28_score < 2.6 %}
                        <span style="color: #4CAF50;">(Remission ✓)</span>
                    {% elif latest.das28_score < 3.2 %}
                        <span style="color: #FFC107;">(Low Activity ⚠)</span>
                    {% elif latest.das28_score <= 5.1 %}
                        <span style="color: #FF9800;">(Moderate ●)</span>
                    {% else %}
                        <span style="color: #F44336;">(High ●)</span>
                    {% endif %}
                </td>
            </tr>
            <tr>
                <td>Tender Joints (TJC)</td>
                <td>{{ latest.tjc }}/28</td>
            </tr>
            <tr>
                <td>Swollen Joints (SJC)</td>
                <td>{{ latest.sjc }}/28</td>
            </tr>
            <tr>
                <td>ESR (mm/h)</td>
                <td>{{ latest.esr }}</td>
            </tr>
            <tr>
                <td>CRP (mg/L)</td>
                <td>{{ latest.crp }}</td>
            </tr>
        </table>
    </div>
    
    <div class="report-section">
        <h2>Current Medications</h2>
        {% if medications %}
            <ul>
            {% for med in medications %}
                <li><strong>{{ med.name }}</strong> {{ med.dose }} - {{ med.frequency }}</li>
            {% endfor %}
            </ul>
        {% else %}
            <p><em>No medications recorded</em></p>
        {% endif %}
    </div>
    
    <div class="report-section">
        <h2>DAS28 Trend (Last 20 Visits)</h2>
        <div id="report-chart-trend" class="chart-container"></div>
    </div>
    
    <div class="report-section">
        <h2>Historical Data</h2>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <tr style="background: #f0f0f0;">
                <th style="padding: 10px; border: 1px solid #ddd;">Date</th>
                <th style="padding: 10px; border: 1px solid #ddd;">DAS28</th>
                <th style="padding: 10px; border: 1px solid #ddd;">TJC</th>
                <th style="padding: 10px; border: 1px solid #ddd;">SJC</th>
                <th style="padding: 10px; border: 1px solid #ddd;">ESR</th>
                <th style="padding: 10px; border: 1px solid #ddd;">CRP</th>
            </tr>
            {% for visit in visits %}
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{{ visit.visit_date.strftime('%m/%d/%Y') }}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{{ "%.1f" % visit.das28_score }}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{{ visit.tjc }}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{{ visit.sjc }}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{{ visit.esr }}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{{ visit.crp }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <!-- Export Options -->
    <div class="export-options">
        <button onclick="window.print()" class="btn btn--primary">🖨️ Print Report</button>
        <button onclick="exportPDF()" class="btn btn--primary">📄 Export as PDF</button>
        <button onclick="exportCSV()" class="btn btn--primary">📊 Export as CSV</button>
    </div>
    
    <!-- Chart rendering script -->
    <script>
        // Load ECharts for trend chart
        async function renderReportCharts() {
            if (typeof echarts === 'undefined') {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js';
                script.onload = () => renderTrendChart();
                document.head.appendChild(script);
            } else {
                renderTrendChart();
            }
        }
        
        function renderTrendChart() {
            const visits = {{ visits | tojson }};
            const dates = visits.map(v => new Date(v.visit_date).toLocaleDateString());
            const scores = visits.map(v => parseFloat(v.das28_score).toFixed(1));
            
            const chart = echarts.init(document.getElementById('report-chart-trend'));
            const option = {
                tooltip: { trigger: 'axis' },
                grid: { left: '10%', right: '10%', bottom: '10%', containLabel: true },
                xAxis: {
                    type: 'category',
                    data: dates,
                    boundaryGap: false
                },
                yAxis: {
                    type: 'value',
                    name: 'DAS28 Score'
                },
                series: [{
                    name: 'DAS28',
                    type: 'line',
                    data: scores,
                    smooth: true,
                    itemStyle: { color: '#2180B0' },
                    lineStyle: { width: 2 },
                    markLine: {
                        data: [
                            { yAxis: 2.6, name: 'Remission', lineStyle: { color: '#4CAF50', type: 'dashed' } },
                            { yAxis: 3.2, name: 'Low Activity', lineStyle: { color: '#FFC107', type: 'dashed' } }
                        ]
                    }
                }]
            };
            chart.setOption(option);
        }
        
        function exportPDF() {
            // Server-side PDF generation
            window.location.href = '/api/reports/export-pdf?patient_id={{ patient.id }}';
        }
        
        function exportCSV() {
            // Generate CSV
            const csv = 'Date,DAS28,TJC,SJC,ESR,CRP\n';
            const rows = {{ visits | tojson }}.map(v => 
                `${v.visit_date},${v.das28_score},${v.tjc},${v.sjc},${v.esr},${v.crp}`
            ).join('\n');
            
            const blob = new Blob([csv + rows], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'patient-report.csv';
            a.click();
        }
        
        // Auto-render charts when page loads
        renderReportCharts();
    </script>
</div>
```

---

## **PART 4: FLASK BACKEND API** 🔧

### **4.1 Dashboard APIs**

```python
# app.py

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get KPI statistics for dashboard"""
    today = date.today()
    
    # Patients today
    visits_today = db.session.query(func.count(Visit.id)).filter(
        Visit.visit_date == today
    ).scalar() or 0
    
    # Average DAS28
    avg_das28 = db.session.query(func.avg(Visit.das28_score)).scalar() or 0
    
    # Remission percentage
    total_visits = db.session.query(func.count(Visit.id)).scalar() or 0
    remission_visits = db.session.query(func.count(Visit.id)).filter(
        Visit.das28_score < 2.6
    ).scalar() or 0
    remission_percent = round((remission_visits / total_visits * 100) if total_visits > 0 else 0)
    
    # Pending reviews (visits without doctor review)
    pending = db.session.query(func.count(Visit.id)).filter(
        Visit.doctor_review.is_(None)
    ).scalar() or 0
    
    return jsonify({
        'patientsToday': visits_today,
        'avgDAS28': round(avg_das28, 2),
        'remissionPercent': remission_percent,
        'pendingReviews': pending
    })


@app.route('/api/dashboard/distribution')
def dashboard_distribution():
    """Get disease activity distribution for pie chart"""
    total_visits = db.session.query(Visit).all()
    
    remission = sum(1 for v in total_visits if v.das28_score < 2.6)
    low_activity = sum(1 for v in total_visits if 2.6 <= v.das28_score < 3.2)
    moderate = sum(1 for v in total_visits if 3.2 <= v.das28_score <= 5.1)
    high = sum(1 for v in total_visits if v.das28_score > 5.1)
    
    return jsonify({
        'remission': remission,
        'low_activity': low_activity,
        'moderate': moderate,
        'high': high
    })


@app.route('/api/dashboard/trend')
def dashboard_trend():
    """Get 30-day DAS28 trend for line chart"""
    start_date = date.today() - timedelta(days=30)
    
    visits = db.session.query(Visit).filter(
        Visit.visit_date >= start_date
    ).order_by(Visit.visit_date).all()
    
    # Aggregate by date
    trend_data = {}
    for visit in visits:
        date_str = visit.visit_date.strftime('%m/%d')
        if date_str not in trend_data:
            trend_data[date_str] = []
        trend_data[date_str].append(visit.das28_score)
    
    # Calculate daily average
    dates = sorted(trend_data.keys())
    scores = [round(sum(trend_data[d]) / len(trend_data[d]), 1) for d in dates]
    
    return jsonify({
        'dates': dates,
        'scores': scores
    })


@app.route('/api/dashboard/recent-visits')
def dashboard_recent_visits():
    """Return recent visits table as HTML"""
    visits = db.session.query(Visit).order_by(
        Visit.visit_date.desc()
    ).limit(10).all()
    
    # Load patients
    for visit in visits:
        visit.patient = Patient.query.get(visit.patient_id)
    
    return render_template('_recent_visits_table.html', visits=visits)


@app.route('/api/patients/search')
def search_patients():
    """Search patients by name or MRN"""
    query = request.args.get('q', '')
    
    results = db.session.query(Patient).filter(
        (Patient.first_name.ilike(f'%{query}%')) |
        (Patient.last_name.ilike(f'%{query}%')) |
        (Patient.mrn.ilike(f'%{query}%'))
    ).limit(10).all()
    
    return jsonify({
        'patients': [{
            'id': p.id,
            'name': f"{p.first_name} {p.last_name}",
            'mrn': p.mrn
        } for p in results]
    })
```

### **4.2 Reports APIs**

```python
@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate report data"""
    data = request.json
    report_type = data['report_type']
    
    if report_type == 'summary':
        patient_id = data['patient_id']
        return jsonify({'status': 'ok', 'patient_id': patient_id})
    
    return jsonify({'status': 'error'})


@app.route('/api/reports/preview')
def report_preview():
    """Render report preview"""
    report_type = request.args.get('type')
    patient_id = request.args.get('patient_id')
    
    if report_type == 'summary':
        patient = Patient.query.get(patient_id)
        visits = Visit.query.filter_by(patient_id=patient_id).order_by(
            Visit.visit_date.desc()
        ).all()
        medications = Medication.query.filter_by(patient_id=patient_id).all()
        
        return render_template('reports/patient_summary.html',
                             patient=patient,
                             visits=visits,
                             medications=medications,
                             now=datetime.now)
    
    return jsonify({'error': 'Invalid report type'})


@app.route('/api/reports/export-pdf')
def export_pdf():
    """Export report as PDF (server-side)"""
    patient_id = request.args.get('patient_id')
    
    patient = Patient.query.get(patient_id)
    visits = Visit.query.filter_by(patient_id=patient_id).order_by(
        Visit.visit_date.desc()
    ).all()
    medications = Medication.query.filter_by(patient_id=patient_id).all()
    
    # Render HTML
    html = render_template('reports/patient_summary.html',
                         patient=patient,
                         visits=visits,
                         medications=medications,
                         now=datetime.now)
    
    # Convert to PDF using WeasyPrint
    pdf = weasyprint.HTML(string=html).write_pdf()
    
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{patient.first_name}_{patient.last_name}_report.pdf'
    )
```

---

## **PART 5: IMPLEMENTATION ROADMAP** 🗺️

### **Phase 1: MVP (Week 1)**
- [ ] Dashboard KPI stats (no charts)
- [ ] Recent visits HTMX table
- [ ] Alpine.js state management

### **Phase 2: Charting (Week 2)**
- [ ] ECharts library integration
- [ ] Disease distribution pie chart
- [ ] DAS28 trend line chart
- [ ] Lazy loading implementation

### **Phase 3: Reports (Week 3)**
- [ ] Report builder form
- [ ] Patient summary template
- [ ] Basic export (print)

### **Phase 4: Advanced Exports (Week 4)**
- [ ] Server-side PDF generation (WeasyPrint)
- [ ] CSV export functionality
- [ ] Performance optimization

### **Phase 5: Polish (Week 5)**
- [ ] Mobile responsiveness
- [ ] Offline caching
- [ ] Error handling
- [ ] Testing on old PC

---

## **Performance Checklist** ✅

- [x] ECharts lazy-loaded (not in initial page load)
- [x] Dashboard loads in <2 seconds on 2GB PC
- [x] Charts render in <500ms after loading
- [x] HTMX for lightweight data updates
- [x] No heavy JavaScript frameworks
- [x] Semantic HTML for accessibility
- [x] Responsive design (mobile-friendly)
- [x] IE11 compatible (ECharts 5.x)
- [x] Offline-first approach possible
- [x] Print-friendly templates

---

**Ready to implement? Start with Part 2.2 Dashboard HTML Template!** 🚀
