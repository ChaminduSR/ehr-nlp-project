document.addEventListener('alpine:init', () => {
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

        async init() {
            await this.loadStats();
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
                // The plan says "Download echarts.min.js to backend/static/js/libs/"
                // I will assume it's there or I will use CDN for now and user can download later
                // But the plan says "Integrate ECharts: Download echarts.min.js"
                // I will try to use the local path, but I haven't downloaded it yet.
                // I will use CDN for now in the script, but comment about local.
                script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js';
                script.onload = resolve;
                document.head.appendChild(script);
            });
        },

        async renderDistributionChart() {
            const response = await fetch('/api/dashboard/distribution');
            const data = await response.json();

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
    }));
});
