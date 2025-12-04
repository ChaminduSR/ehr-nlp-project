function medicalNote() {
    return {
      smartText: '',
      isRecording: false,
      isExtracting: false,
      showReview: false,
      reviewData: {},
      error: null,
      visitId: new URLSearchParams(window.location.search).get('visit_id'),

      formatKey(key) {
        return key.replace(/_/g, ' ');
      },

      async toggleRecording() {
        if (this.isRecording) {
          // Stop Recording
          try {
            const text = await window.VoiceRecorder.stop();
            if (text) {
              this.smartText += (this.smartText ? ' ' : '') + text;
            }
          } catch (err) {
            console.error(err);
            this.error = 'Transcription failed: ' + err;
          } finally {
            this.isRecording = false;
          }
        } else {
          // Start Recording
          const started = await window.VoiceRecorder.start();
          if (started) {
            this.isRecording = true;
          }
        }
      },

      async extractEntities() {
        if (!this.smartText) return;
        this.isExtracting = true;
        this.error = null;
        try {
          const res = await fetch('/api/v1/medical_notes/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: this.smartText })
          });
          const data = await res.json();
          if (data.success) {
            this.reviewData = data.structured;
            this.showReview = true;
          } else {
            this.error = 'Extraction failed: ' + (data.message || 'Unknown error');
          }
        } catch (e) {
          console.error(e);
          this.error = 'Failed to connect to extraction service.';
        } finally {
          this.isExtracting = false;
        }
      },

      async acceptExtraction() {
        if (!this.visitId) {
          this.error = 'No visit selected. Cannot save.';
          return;
        }

        try {
          // Convert structured data to Note Text format (Sections)
          const SECTION_MAPPING = {
            chief_complaint: 'CHIEF COMPLAINT',
            hpi: 'HISTORY OF PRESENT ILLNESS',
            physical_exam: 'PHYSICAL EXAMINATION',
            assessment: 'ASSESSMENT',
            plan: 'PLAN',
            medications: 'MEDICATIONS',
            follow_up: 'FOLLOW-UP'
          };

          let noteText = '';
          for (const [key, value] of Object.entries(this.reviewData)) {
            const header = SECTION_MAPPING[key];
            if (header && value) {
              noteText += `${header}:\n${value}\n\n`;
            }
          }

          // Save to backend
          const res = await fetch('/api/v1/medical_notes/draft', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              visit_id: this.visitId,
              text: noteText
            })
          });

          if (res.ok) {
            this.showReview = false;
            this.smartText = '';
            this.reviewData = {};
            // Trigger HTMX refresh
            document.body.dispatchEvent(new Event('refreshReport'));
          } else {
            this.error = 'Failed to save data.';
          }

        } catch (e) {
          console.error(e);
          this.error = 'An error occurred while saving.';
        }
      }
    }
  }
