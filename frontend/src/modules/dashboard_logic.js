// Simple cache with TTL (10 minutes)
const CACHE_TTL = 10 * 60 * 1000;
const cache = {
    get(key) {
        const item = sessionStorage.getItem(`dashboard_${key}`);
        if (!item) return null;
        const { data, timestamp } = JSON.parse(item);
        if (Date.now() - timestamp > CACHE_TTL) {
            sessionStorage.removeItem(`dashboard_${key}`);
            return null;
        }
        return data;
    },
    set(key, data) {
        sessionStorage.setItem(`dashboard_${key}`, JSON.stringify({ data, timestamp: Date.now() }));
    }
};

export function initDashboard(Alpine) {
    Alpine.data('dashboardData', () => ({
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
        isLoading: false,

        async init() {
            await this.loadStats();
        },

        async loadStats(forceRefresh = false) {
            // Check cache first
            if (!forceRefresh) {
                const cached = cache.get('stats');
                if (cached) {
                    this.stats = cached;
                    return;
                }
            }

            this.isLoading = true;
            try {
                const response = await fetch('/api/v1/dashboard/stats');
                const data = await response.json();
                this.stats = data;
                cache.set('stats', data);
            } catch (error) {
                console.error('Error loading stats:', error);
            } finally {
                this.isLoading = false;
            }
        },

        refreshStats() {
            return this.loadStats(true);
        },

        async loadChart(type) {
            // Check if ECharts is already loaded
            if (typeof echarts === 'undefined') {
                await this.loadECharts();
            }

            if (type === 'distribution') {
                this.charts.distribution = true;
                // Wait for DOM update
                this.$nextTick(() => {
                    this.renderDistributionChart();
                });
            } else if (type === 'trend') {
                this.charts.trend = true;
                this.$nextTick(() => {
                    this.renderTrendChart();
                });
            }
        },

        async loadECharts() {
            return new Promise((resolve) => {
                const script = document.createElement('script');
                // Use local file if available, fallback to CDN or just use CDN for now as per plan
                script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js';
                script.onload = resolve;
                document.head.appendChild(script);
            });
        },

        async renderDistributionChart() {
            // Check cache first
            let data = cache.get('distribution');
            if (!data) {
                const response = await fetch('/api/v1/dashboard/distribution');
                data = await response.json();
                cache.set('distribution', data);
            }

            // Get colors from CSS variables
            const style = getComputedStyle(document.body);
            const colorRemission = style.getPropertyValue('--color-remission').trim();
            const colorLow = style.getPropertyValue('--color-low-activity').trim();
            const colorModerate = style.getPropertyValue('--color-moderate').trim();
            const colorHigh = style.getPropertyValue('--color-high').trim();

            const chartDom = document.getElementById('chart-distribution');
            const chart = echarts.init(chartDom);
            const option = {
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
                        { value: data.remission, name: 'Remission', itemStyle: { color: colorRemission } },
                        { value: data.low_activity, name: 'Low Activity', itemStyle: { color: colorLow } },
                        { value: data.moderate, name: 'Moderate', itemStyle: { color: colorModerate } },
                        { value: data.high, name: 'High', itemStyle: { color: colorHigh } }
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
            // Check cache first
            let data = cache.get('trend');
            if (!data) {
                const response = await fetch('/api/v1/dashboard/trend');
                data = await response.json();
                cache.set('trend', data);
            }

            // Get colors from CSS variables
            const style = getComputedStyle(document.body);
            const colorRemission = style.getPropertyValue('--color-remission').trim();
            const colorLow = style.getPropertyValue('--color-low-activity').trim();
            const colorHigh = style.getPropertyValue('--color-high').trim();
            const colorPrimary = style.getPropertyValue('--pico-primary').trim() || '#2180B0';

            const chartDom = document.getElementById('chart-trend');
            const chart = echarts.init(chartDom);
            const option = {
                tooltip: {
                    trigger: 'axis',
                    formatter: '{b0}<br/>{a0}: {c0}'
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: data.dates,
                    boundaryGap: false
                },
                yAxis: {
                    type: 'value',
                    name: 'DAS28 Score'
                },
                series: [{
                    name: 'Average DAS28',
                    type: 'line',
                    data: data.scores,
                    smooth: true,
                    itemStyle: { color: colorPrimary },
                    lineStyle: { width: 2 },
                    markLine: {
                        data: [
                            { yAxis: 2.6, name: 'Remission', lineStyle: { color: colorRemission } },
                            { yAxis: 3.2, name: 'Low Activity', lineStyle: { color: colorLow } },
                            { yAxis: 5.1, name: 'High Activity', lineStyle: { color: colorHigh } }
                        ]
                    }
                }]
            };

            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }
    }));
}
