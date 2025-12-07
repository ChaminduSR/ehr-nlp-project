export function medicalNote() {
    return {
      smartText: '',
      isRecording: false,
      isExtracting: false,
      showReview: false,
      reviewData: {},
      error: null,
      visitId: new URLSearchParams(window.location.search).get('visit_id'),
      lastSavedText: '',
      saveStatus: '', // 'Saving...', 'Saved', 'Error'

      init() {
        // Note: Auto-save is handled by medical_note_form.html fragment (30s interval)
        // This module only listens for save events to update UI state

        // Sync Smart Detection textarea into this.smartText so coordinatedSave sees latest text
        try {
          const ta = document.getElementById('dictation-input');
          if (ta) {
            ta.addEventListener('input', () => {
              this.smartText = ta.value;
              // mark fragment dirty if helper exists
              if (window._markDirty) window._markDirty();
            });
          }
        } catch (e) {
          // ignore if fragment not loaded
        }
        // Listen for coordinated save events to reflect a singleton save status
        window.addEventListener('coordinatedSaveStart', () => {
          this.saveStatus = 'Saving...';
        });

        window.addEventListener('coordinatedSaveEnd', (e) => {
          try {
            const ok = e && e.detail && e.detail.success;
            if (ok) {
              this.lastSavedText = this.smartText;
              this.saveStatus = 'Saved';
              setTimeout(() => { this.saveStatus = ''; }, 3000);
            } else {
              this.saveStatus = 'Error saving draft';
            }
          } catch (err) {
            console.warn('coordinatedSaveEnd handler error', err);
            this.saveStatus = '';
          }
        });
      },

      async autoSave() {
        // Auto-save is handled by the fragment's coordinatedSave
        // This is kept as a fallback only if the fragment isn't loaded
        if (window.coordinatedSave && typeof window.coordinatedSave === 'function') {
          // Let the fragment handle it - don't duplicate saves
          return;
        }

        // Fallback: direct save only if fragment not loaded
        if (!this.visitId || !this.smartText || this.smartText === this.lastSavedText) {
          return;
        }

        this.saveStatus = 'Saving...';
        try {
          const res = await fetch('/api/v1/medical_notes/draft', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              visit_id: this.visitId,
              text: this.smartText
            })
          });

          if (res.ok) {
            this.lastSavedText = this.smartText;
            this.saveStatus = 'Saved';
            setTimeout(() => { this.saveStatus = ''; }, 3000);
          } else {
            this.saveStatus = 'Error saving draft';
          }
        } catch (e) {
          console.error(e);
          this.saveStatus = 'Error saving draft';
        }
      },

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
              // Also update fragment textarea if present so both UIs stay in sync
              try {
                const ta = document.getElementById('dictation-input');
                if (ta) {
                  ta.value = this.smartText;
                  ta.dispatchEvent(new Event('input', { bubbles: true }));
                }
              } catch (e) {}
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
            // Wait briefly for the review UI to render/appear so the extracting
            // state remains active until the user sees the review window.
            // This polls the reactive flag and lets the browser render one frame.
            try {
              await this.waitForReviewToShow(3000);
            } catch (err) {
              // If waiting fails or times out, continue and clear extracting flag below.
              console.warn('waitForReviewToShow timed out or failed', err);
            }
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

      // Wait until the review UI has been requested to show and allow a
      // short rendering window so the modal/dialog becomes visible.
      async waitForReviewToShow(timeout = 3000) {
        const start = Date.now();
        // Poll for the `showReview` reactive flag which controls the modal.
        while ((Date.now() - start) < timeout) {
          if (this.showReview) {
            // Give the browser a frame and a small delay to render the modal
            await new Promise((r) => requestAnimationFrame(r));
            await new Promise((r) => setTimeout(r, 80));
            return true;
          }
          await new Promise((r) => setTimeout(r, 50));
        }
        throw new Error('timeout waiting for review UI');
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
              // Handle both strings and arrays (arrays were converted to comma-separated strings in the UI)
              const textValue = Array.isArray(value) ? value.join(', ') : value;
              if (textValue.trim()) {
                noteText += `${header}:\n${textValue}\n\n`;
              }
            }
          }

          // Prefer coordinated save: populate fragment inputs (if present) and call coordinatedSave
          try {
            const inputs = document.querySelectorAll('.note-section');
            const mapping = SECTION_MAPPING;
            if (inputs && inputs.length > 0) {
              inputs.forEach(input => {
                const section = input.dataset.section;
                const key = Object.keys(mapping).find(k => mapping[k] === section);
                if (key && this.reviewData && this.reviewData[key]) {
                  const value = Array.isArray(this.reviewData[key]) ? this.reviewData[key].join(', ') : this.reviewData[key];
                  input.value = value;
                }
              });
            }

            // Clear dictation smartText and dictation textarea so coordinated save captures structured inputs
            this.smartText = '';
            try {
              const ta = document.getElementById('dictation-input');
              if (ta) { ta.value = ''; ta.dispatchEvent(new Event('input', { bubbles: true })); }
            } catch (e) {}

            if (window.coordinatedSave && typeof window.coordinatedSave === 'function') {
              await window.coordinatedSave();
            } else {
              // fallback to direct save if coordinated is not available
              const res = await fetch('/api/v1/medical_notes/draft', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ visit_id: this.visitId, text: noteText })
              });
              if (!res.ok) throw new Error('Failed to save');
            }

            this.showReview = false;
            this.reviewData = {};
            // Trigger HTMX refresh
            document.body.dispatchEvent(new Event('refreshReport'));
          } catch (e) {
            console.error(e);
            this.error = 'Failed to save data.';
          }

        } catch (e) {
          console.error(e);
          this.error = 'An error occurred while saving.';
        }
      }
    }
  }
