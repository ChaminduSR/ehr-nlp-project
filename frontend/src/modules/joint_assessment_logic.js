export function jointAssessment() {
    return {
      tjc: 0,
      sjc: 0,
      esr: 20,
      pga: 50,
      score: 0,

      // State
      joints: {}, // id -> { tenderness: bool, pain: bool, swelling: int }
      lastSavedJson: '',
      saveStatus: '',

      // Tooltip
      hoveredJoint: null,
      tooltipX: 0,
      tooltipY: 0,

      init() {
        // Initialize Konva
        window.JointDiagram.init(
          'joint-canvas',
          (id, x, y) => this.handleJointClick(id), // Click
          (data, x, y) => this.handleHover(data, x, y), // Hover
          (id, x, y) => this.handleJointRightClick(id) // Right Click
        );

        // Initialize joints state
        window.JointDiagram.jointData.forEach(j => {
          this.joints[j.id] = { tenderness: false, pain: false, swelling: 0 };
        });

        // Load existing data
        this.loadExistingData();

        this.calculateDAS28();

        // Auto-save every 30 seconds
        setInterval(() => {
          this.autoSave();
        }, 30000);
      },

      handleHover(data, x, y) {
        if (data) {
          this.hoveredJoint = data;
          // Adjust for canvas position relative to viewport
          const rect = document.getElementById('joint-canvas').getBoundingClientRect();
          this.tooltipX = rect.left + x;
          this.tooltipY = rect.top + y;
        } else {
          this.hoveredJoint = null;
        }
      },

      handleJointClick(id) {
        const joint = this.joints[id];
        // Cycle: Normal (0) -> Tenderness (1) -> Swelling (2) -> Both (3) -> Normal (0)
        // We determine current state based on properties
        let currentState = 0;
        if (joint.tenderness && joint.swelling > 0) currentState = 3;
        else if (joint.swelling > 0) currentState = 2;
        else if (joint.tenderness) currentState = 1;
        else currentState = 0;

        let nextState = (currentState + 1) % 4;

        // Apply next state
        switch (nextState) {
          case 0: // Normal
            joint.tenderness = false;
            joint.swelling = 0;
            break;
          case 1: // Tenderness (Yellow)
            joint.tenderness = true;
            joint.swelling = 0;
            break;
          case 2: // Swelling (Red)
            joint.tenderness = false;
            joint.swelling = 1; // Default to mild swelling
            break;
          case 3: // Both (Orange)
            joint.tenderness = true;
            joint.swelling = 1;
            break;
        }

        // Update Visuals
        window.JointDiagram.updateJointState(id, joint);
        // Update Counts
        this.updateCounts();
      },

      handleJointRightClick(id) {
        const joint = this.joints[id];
        joint.pain = !joint.pain;

        // Update Visuals
        window.JointDiagram.updateJointState(id, joint);
        // Update Counts
        this.updateCounts();
      },

      updateCounts() {
        let t = 0;
        let s = 0;
        Object.values(this.joints).forEach(j => {
          if (j.tenderness) t++;
          if (j.swelling > 0) s++;
        });
        this.tjc = t;
        this.sjc = s;
        this.calculateDAS28();
      },

      calculateDAS28() {
        // DAS28-ESR formula
        // 0.56 * sqrt(TJC) + 0.28 * sqrt(SJC) + 0.70 * ln(ESR) + 0.014 * PGA
        const t = Math.sqrt(this.tjc) * 0.56;
        const s = Math.sqrt(this.sjc) * 0.28;
        const e = Math.log(Math.max(1, this.esr)) * 0.70; // Ensure log(>0)
        const p = this.pga * 0.014;
        this.score = (t + s + e + p).toFixed(2);
      },

      async autoSave() {
        const currentJson = JSON.stringify(this.joints);
        if (currentJson === this.lastSavedJson) return;

        await this.saveAssessment(true);
      },

      async saveAssessment(silent = false) {
        const visitId = new URLSearchParams(window.location.search).get('visit_id');
        if (!visitId) {
          if (!silent) alert('No Visit ID found!');
          return;
        }

        const payload = {
          visit_id: visitId,
          joints: Object.entries(this.joints).map(([id, state]) => ({
            joint_id: id,
            has_tenderness: state.tenderness,
            has_pain: state.pain,
            swelling_grade: state.swelling
          }))
        };

        this.saveStatus = 'Saving...';

        try {
          const res = await fetch('/api/v1/joint_assessments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });

          if (res.ok) {
            this.lastSavedJson = JSON.stringify(this.joints);
            this.saveStatus = 'Saved';
            setTimeout(() => { this.saveStatus = ''; }, 3000);
            if (!silent) alert('Assessment saved successfully!');
          } else {
            this.saveStatus = 'Error';
            if (!silent) alert('Error saving assessment');
          }
        } catch (err) {
          console.error(err);
          this.saveStatus = 'Error';
          if (!silent) alert('Network error');
        }
      },

      async loadExistingData() {
        const visitId = new URLSearchParams(window.location.search).get('visit_id');
        if (!visitId) return;

        try {
          const res = await fetch(`/api/v1/joint_assessments/visit/${visitId}`);
          const data = await res.json();

          if (data.joints && data.joints.length > 0) {
            data.joints.forEach(row => {
              // Map DB columns to our state
              // DB: joint_id, has_tenderness, has_pain, swelling_grade
              // State: tenderness, pain, swelling
              if (this.joints[row.joint_id]) {
                this.joints[row.joint_id] = {
                  tenderness: Boolean(row.has_tenderness),
                  pain: Boolean(row.has_pain),
                  swelling: parseInt(row.swelling_grade || 0)
                };
                // Update visual
                window.JointDiagram.updateJointState(row.joint_id, this.joints[row.joint_id]);
              }
            });
            this.updateCounts();
          }
        } catch (err) {
          console.error("Failed to load existing data", err);
        }
      }
    }
  }
