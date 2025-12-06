export function patientsManager() {
    return {
      patients: [],
      filteredPatients: [],
      searchQuery: '',
      isModalOpen: false,
      isEditMode: false,
      form: {
        id: null,
        mrn: '',
        first_name: '',
        last_name: '',
        date_of_birth: ''
      },

      async init() {
        await this.fetchPatients();
      },

      async fetchPatients() {
        try {
          const res = await fetch('/api/v1/patients');
          this.patients = await res.json();
          this.filterPatients();
        } catch (e) {
          console.error("Failed to fetch patients", e);
        }
      },

      filterPatients() {
        if (!this.searchQuery) {
          this.filteredPatients = this.patients;
          return;
        }
        const q = this.searchQuery.toLowerCase();
        this.filteredPatients = this.patients.filter(p =>
          p.mrn.toLowerCase().includes(q) ||
          p.first_name.toLowerCase().includes(q) ||
          p.last_name.toLowerCase().includes(q)
        );
      },

      openAddModal() {
        this.isEditMode = false;
        this.form = { id: null, mrn: '', first_name: '', last_name: '', date_of_birth: '' };
        this.isModalOpen = true;
      },

      openEditModal(patient) {
        this.isEditMode = true;
        this.form = { ...patient };
        this.isModalOpen = true;
      },

      closeModal() {
        this.isModalOpen = false;
      },

      async savePatient() {
        const url = this.isEditMode ? `/api/v1/patients/${this.form.id}` : '/api/v1/patients';
        const method = this.isEditMode ? 'PUT' : 'POST';

        try {
          const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.form)
          });

          if (res.ok) {
            await this.fetchPatients();
            this.closeModal();
          } else {
            alert('Failed to save patient.');
          }
        } catch (e) {
          console.error(e);
          alert('Error saving patient.');
        }
      },

      async createNewVisit(patientId) {
        if (!confirm('Create a new visit for today?')) return;

        const today = new Date().toISOString().split('T')[0];
        try {
          const res = await fetch('/api/v1/visits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              patient_id: patientId,
              visit_date: today,
              visit_type: 'Follow-up'
            })
          });

          if (res.ok) {
            const data = await res.json();
            window.location.href = `/medical-note?visit_id=${data.id}`;
          } else {
            alert('Failed to create visit.');
          }
        } catch (e) {
          console.error(e);
          alert('Error creating visit.');
        }
      }
    }
  }
