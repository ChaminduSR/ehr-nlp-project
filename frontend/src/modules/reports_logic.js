export function initReports(Alpine) {
    Alpine.data('reportsLogic', () => ({
        reportType: 'summary',
        selectedPatient: null,
        patientResults: [],
        filters: {
            startDate: '',
            endDate: ''
        },
        isGenerating: false,
        showPreview: false,

        init() {
            // Default date range: Last 30 days
            const today = new Date();
            const lastMonth = new Date();
            lastMonth.setDate(today.getDate() - 30);

            this.filters.endDate = today.toISOString().split('T')[0];
            this.filters.startDate = lastMonth.toISOString().split('T')[0];
        },

        updateForm() {
            this.patientResults = [];
            this.selectedPatient = null;
            this.showPreview = false;
        },

        async searchPatients(event) {
            const query = event.target.value;
            if (query.length < 2) {
                this.patientResults = [];
                return;
            }

            try {
                const response = await fetch(`/api/v1/patients/search?q=${encodeURIComponent(query)}`);
                if (response.ok) {
                    const data = await response.json();
                    this.patientResults = data;
                } else {
                    // Fallback mock
                    this.patientResults = [
                        { id: 1, name: 'John Doe', mrn: 'MRN-123' },
                        { id: 2, name: 'Jane Smith', mrn: 'MRN-456' }
                    ].filter(p => p.name.toLowerCase().includes(query.toLowerCase()));
                }
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
            this.showPreview = false;

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

                // Show preview container
                this.showPreview = true;

                // Trigger HTMX to load preview
                this.$nextTick(() => {
                    const previewDiv = document.getElementById('report-preview').firstElementChild;
                    let url = `/api/reports/preview?type=${this.reportType}`;
                    if (this.selectedPatient) {
                        url += `&patient_id=${this.selectedPatient.id}`;
                    }
                    previewDiv.setAttribute('hx-get', url);
                    htmx.process(previewDiv);
                    htmx.trigger(previewDiv, 'manual');

                    document.getElementById('report-preview').scrollIntoView({ behavior: 'smooth' });
                });

            } catch (error) {
                console.error('Error:', error);
                alert('Error generating report');
            } finally {
                this.isGenerating = false;
            }
        }
    }));
}
