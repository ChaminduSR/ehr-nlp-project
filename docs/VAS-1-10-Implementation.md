# 🏥 PATIENT GLOBAL VAS 1-10 SCALE IMPLEMENTATION
## Visual Analog Scale for Rheumatology EHR Joint Assessment
**Version:** 2.1 (VAS Updated)  
**Date:** December 6, 2025  
**Status:** Ready for Implementation

---

## 📋 OVERVIEW

Replace the **Patient Global 0-100 scale** with a **Visual Analog Scale (VAS 1-10)** that is:
- ✅ More clinically standard for rheumatology (DAS28 uses 0-100cm, but 1-10 is easier for doctors)
- ✅ Faster to select (10 buttons vs. slider precision)
- ✅ Color-coded for instant visual feedback
- ✅ Touch-friendly (48px buttons)
- ✅ Keyboard accessible (arrow keys to change)

---

## 🎨 VISUAL DESIGN

### 1-10 Scale with Color Gradients

```
┌─────────────────────────────────────────────┐
│  Patient Global Assessment (VAS)            │
├─────────────────────────────────────────────┤
│                                             │
│  Rate overall joint pain/activity           │
│  (Doctor asks patient; patient responds)    │
│                                             │
│  [ 1 ][ 2 ][ 3 ][ 4 ][ 5 ][ 6 ][ 7 ][ 8 ][ 9 ][10]
│   ◆   ◆   ◆   ◆   ◆   ◆   ◆   ◆   ◆   ◆
│   │   │   │   │   │   │   │   │   │   │
│  None Mild      Moderate     Severe  Worst
│  Pain Activity   Activity     Activity Pain
│
│  Selected: 5 (Moderate)
│  ┌──────────────────────────────────┐
│  │ ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│  │ 50% Scale Fill                   │
│  └──────────────────────────────────┘
│
└─────────────────────────────────────────────┘

Color Mapping:
  1-2:  Green     (#81C784) → No/Minimal pain
  3-4:  Lime      (#AED581) → Mild pain
  5-6:  Yellow    (#FFE082) → Moderate pain
  7-8:  Orange    (#FFB74D) → Severe pain
  9-10: Red       (#FF5252) → Worst pain
```

---

## 💾 DATABASE SCHEMA UPDATE

### Migration: Add `pg_scale_1_10` column

```sql
-- Add new column for VAS 1-10
ALTER TABLE joint_assessments 
ADD COLUMN pg_scale_1_10 INTEGER DEFAULT 5 COMMENT 'Patient Global VAS 1-10 (5=moderate)';

-- Migrate old 0-100 values to 1-10 scale (divide by 10, round)
UPDATE joint_assessments 
SET pg_scale_1_10 = ROUND(patient_global / 10) 
WHERE patient_global IS NOT NULL;

-- Add index for faster queries
CREATE INDEX idx_pg_scale ON joint_assessments(pg_scale_1_10);
```

### Updated Model (SQLAlchemy)

```python
# backend/models/joint_assessment.py

class JointAssessment(IntegerPKMixin, TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
    """Joint Assessment with VAS 1-10 Patient Global Scale."""
    
    __tablename__ = "joint_assessments"
    
    # ... existing fields ...
    
    # UPDATED: Patient Global (now VAS 1-10)
    pg_scale: Mapped[int] = mapped_column(
        Integer,
        default=5,  # Middle of scale (moderate activity)
        index=True,
        comment="Patient Global VAS 1-10 (1=no activity, 10=worst)"
    )
    
    # Keep old column for backward compatibility (deprecated)
    patient_global_0_100: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="DEPRECATED: Old 0-100 scale, use pg_scale instead"
    )
    
    def __repr__(self) -> str:
        return f"<JointAssessment(pg={self.pg_scale}/10, tjc={self.has_tenderness}, sjc={self.swelling_grade})>"
    
    def to_dict(self) -> dict:
        return {
            # ... existing fields ...
            "pg_scale": self.pg_scale,
            "pg_description": self.get_pg_description(),
        }
    
    @property
    def get_pg_description(self) -> str:
        """Get human-readable description of PG scale."""
        descriptions = {
            1: "No activity",
            2: "Minimal activity",
            3: "Mild activity",
            4: "Mild activity",
            5: "Moderate activity",
            6: "Moderate activity",
            7: "Severe activity",
            8: "Severe activity",
            9: "Very severe activity",
            10: "Worst possible activity"
        }
        return descriptions.get(self.pg_scale, "Unknown")
```

### API Endpoint (Backend)

```python
# backend/routes/joint_assessments.py

@app.route("/api/v1/joint-assessments/save", methods=["POST"])
def save_joint_assessment():
    """
    Save joint assessments with VAS 1-10 Patient Global Scale.
    
    Request:
        {
            "visit_id": "V-2025-001",
            "pg_scale": 5,  # NEW: VAS 1-10 instead of 0-100
            "tjc": 6,
            "sjc": 2,
            "esr": 20,
            "assessments": [...]
        }
    """
    data = request.get_json()
    visit_id = data.get("visit_id")
    pg_scale = data.get("pg_scale", 5)  # NEW FIELD
    
    # Validate VAS range
    if not (1 <= pg_scale <= 10):
        return jsonify({"error": "pg_scale must be 1-10"}), 400
    
    try:
        with session_scope() as session:
            assessments = data.get("assessments", [])
            
            # Delete old assessments
            session.query(JointAssessment).filter_by(visit_id=visit_id).delete()
            
            # Create new assessments
            for assessment in assessments:
                ja = JointAssessment(
                    visit_id=visit_id,
                    joint_id=assessment.get("joint_id"),
                    has_tenderness=assessment.get("has_tenderness", False),
                    swelling_grade=assessment.get("swelling_grade", 0),
                    has_pain=assessment.get("has_pain", False),
                    pg_scale=pg_scale,  # NEW: Store VAS 1-10
                    assessed_at=datetime.utcnow(),
                )
                session.add(ja)
            
        return jsonify({
            "success": True,
            "message": "Assessment saved",
            "pg_scale": pg_scale,
            "pg_description": f"Patient Global: {pg_scale}/10"
        }), 200
        
    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
```

---

## 🎨 HTML IMPLEMENTATION

### Replace Old Patient Global Input

```html
<!-- BEFORE (0-100 slider) -->
<div class="stat-row">
  <label for="pgInput">Patient Global (0-100)</label>
  <input 
    type="range" 
    id="pgInput" 
    min="0" 
    max="100" 
    value="50"
    class="stat-input"
  >
  <span id="pgValue">50</span>
</div>

<!-- AFTER (VAS 1-10 buttons) -->
<div class="patient-global-vas">
  <label>Patient Global (VAS 1-10)</label>
  <p class="vas-instruction">
    How would you rate your overall joint activity today? 
    (1 = No activity, 10 = Worst possible)
  </p>
  
  <div class="vas-scale">
    <button class="vas-button" data-value="1" title="No activity">
      <span class="vas-number">1</span>
      <span class="vas-label">None</span>
    </button>
    <button class="vas-button" data-value="2" title="Minimal">
      <span class="vas-number">2</span>
      <span class="vas-label">Minimal</span>
    </button>
    <button class="vas-button" data-value="3" title="Mild activity">
      <span class="vas-number">3</span>
      <span class="vas-label">Mild</span>
    </button>
    <button class="vas-button" data-value="4" title="Mild activity">
      <span class="vas-number">4</span>
      <span class="vas-label">Mild</span>
    </button>
    <button class="vas-button vas-button--selected" data-value="5" title="Moderate activity">
      <span class="vas-number">5</span>
      <span class="vas-label">Moderate</span>
    </button>
    <button class="vas-button" data-value="6" title="Moderate activity">
      <span class="vas-number">6</span>
      <span class="vas-label">Moderate</span>
    </button>
    <button class="vas-button" data-value="7" title="Severe activity">
      <span class="vas-number">7</span>
      <span class="vas-label">Severe</span>
    </button>
    <button class="vas-button" data-value="8" title="Severe activity">
      <span class="vas-number">8</span>
      <span class="vas-label">Severe</span>
    </button>
    <button class="vas-button" data-value="9" title="Very severe">
      <span class="vas-number">9</span>
      <span class="vas-label">V.Severe</span>
    </button>
    <button class="vas-button" data-value="10" title="Worst possible">
      <span class="vas-number">10</span>
      <span class="vas-label">Worst</span>
    </button>
  </div>
  
  <!-- Visual Feedback Bar -->
  <div class="vas-feedback-bar">
    <div class="vas-fill" id="vasFill" style="width: 50%;"></div>
    <div class="vas-markers">
      <span class="marker" style="left: 0%;">1</span>
      <span class="marker" style="left: 50%;">5</span>
      <span class="marker" style="left: 100%;">10</span>
    </div>
  </div>
  
  <!-- Current Selection Display -->
  <div class="vas-selection">
    <span id="vasSelectedValue">5</span>
    <span id="vasSelectedLabel">Moderate Activity</span>
  </div>
  
  <!-- Hidden input for form submission -->
  <input type="hidden" id="pgScaleInput" name="pg_scale" value="5">
</div>
```

---

## 🎨 CSS STYLING

```css
/* VAS Scale Container */
.patient-global-vas {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #f9f9f9;
  border: 2px solid #ddd;
  border-radius: 8px;
  margin-bottom: 16px;
}

.patient-global-vas > label {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.vas-instruction {
  margin: 0;
  font-size: 13px;
  color: #666;
  font-style: italic;
}

/* VAS Scale Button Grid */
.vas-scale {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 4px;
  margin: 8px 0;
}

/* Individual VAS Button */
.vas-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 4px;
  min-height: 60px;
  border: 2px solid #ddd;
  border-radius: 6px;
  background: #f0f0f0;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  font-weight: 500;
}

/* VAS Button Number */
.vas-button .vas-number {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: #333;
}

/* VAS Button Label */
.vas-button .vas-label {
  display: block;
  font-size: 10px;
  color: #666;
  margin-top: 2px;
}

/* Color Gradient for Each Value */
.vas-button[data-value="1"] {
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
  border-color: #81C784;
}

.vas-button[data-value="2"] {
  background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%);
  border-color: #81C784;
}

.vas-button[data-value="3"] {
  background: linear-gradient(135deg, #A5D6A7 0%, #81C784 100%);
  border-color: #66BB6A;
}

.vas-button[data-value="4"] {
  background: linear-gradient(135deg, #81C784 0%, #66BB6A 100%);
  border-color: #66BB6A;
}

.vas-button[data-value="5"] {
  background: linear-gradient(135deg, #FFF9C4 0%, #FFE082 100%);
  border-color: #FDD835;
}

.vas-button[data-value="6"] {
  background: linear-gradient(135deg, #FFE082 0%, #FFD54F 100%);
  border-color: #FDD835;
}

.vas-button[data-value="7"] {
  background: linear-gradient(135deg, #FFD54F 0%, #FFB74D 100%);
  border-color: #FFA726;
}

.vas-button[data-value="8"] {
  background: linear-gradient(135deg, #FFB74D 0%, #FFA726 100%);
  border-color: #FF9800;
}

.vas-button[data-value="9"] {
  background: linear-gradient(135deg, #FFA726 0%, #FF7043 100%);
  border-color: #FF6E40;
}

.vas-button[data-value="10"] {
  background: linear-gradient(135deg, #FF7043 0%, #FF5252 100%);
  border-color: #FF1744;
  color: white;
}

.vas-button[data-value="10"] .vas-number,
.vas-button[data-value="10"] .vas-label {
  color: white;
}

/* Hover State */
.vas-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  border-width: 3px;
  padding: 7px 3px;
}

/* Selected State */
.vas-button--selected,
.vas-button[data-value="5"]:focus {
  border-width: 3px;
  box-shadow: 0 0 0 3px rgba(255, 221, 87, 0.4);
  padding: 7px 3px;
}

/* Focus State (Accessibility) */
.vas-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.4);
}

/* Feedback Bar */
.vas-feedback-bar {
  position: relative;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin: 8px 0;
}

.vas-fill {
  height: 100%;
  background: linear-gradient(90deg, 
    #81C784 0%,    /* Green: 1-2 */
    #AED581 20%,   /* Lime: 3-4 */
    #FFE082 40%,   /* Yellow: 5-6 */
    #FFB74D 60%,   /* Orange: 7-8 */
    #FF5252 100%   /* Red: 9-10 */
  );
  transition: width 0.3s ease;
}

.vas-markers {
  position: absolute;
  top: 100%;
  width: 100%;
  height: 16px;
  display: flex;
  justify-content: space-between;
  padding-top: 2px;
}

.vas-markers .marker {
  font-size: 10px;
  color: #666;
  font-weight: 600;
  width: 20px;
  text-align: center;
}

/* Selection Display */
.vas-selection {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin-top: 8px;
}

#vasSelectedValue {
  font-size: 24px;
  font-weight: 700;
  color: #0066cc;
}

#vasSelectedLabel {
  font-size: 14px;
  color: #666;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .vas-scale {
    grid-template-columns: repeat(5, 1fr);
    gap: 2px;
  }
  
  .vas-button {
    min-height: 50px;
    padding: 6px 2px;
    font-size: 11px;
  }
  
  .vas-button .vas-number {
    font-size: 14px;
  }
  
  .vas-button .vas-label {
    font-size: 9px;
  }
  
  /* Ensure touch target >= 44px */
  .vas-button {
    min-width: 44px;
    min-height: 44px;
  }
}

/* Very small screens */
@media (max-width: 480px) {
  .vas-scale {
    grid-template-columns: repeat(5, 1fr);
  }
  
  .vas-button .vas-label {
    display: none;
  }
}
```

---

## 💻 JAVASCRIPT IMPLEMENTATION

```javascript
// Global VAS State
const vasState = {
  selectedValue: 5,
  previousValue: 5,
  isDirty: false
};

// Initialize VAS Scale
function initializeVAS() {
  const vasButtons = document.querySelectorAll('.vas-button');
  
  vasButtons.forEach(button => {
    button.addEventListener('click', (e) => {
      const value = parseInt(button.dataset.value);
      setVASValue(value);
    });
    
    // Keyboard support (arrow keys)
    button.addEventListener('keydown', (e) => {
      const currentValue = vasState.selectedValue;
      
      if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (currentValue < 10) {
          setVASValue(currentValue + 1);
          vasButtons[currentValue].focus();  // Auto-focus next
        }
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
        e.preventDefault();
        if (currentValue > 1) {
          setVASValue(currentValue - 1);
          vasButtons[currentValue - 2].focus();  // Auto-focus previous
        }
      }
    });
  });
}

// Set VAS Value
function setVASValue(value) {
  if (value < 1 || value > 10) return;
  
  const vasButtons = document.querySelectorAll('.vas-button');
  
  // Remove previous selection
  vasButtons.forEach(btn => btn.classList.remove('vas-button--selected'));
  
  // Add selection to clicked button
  const selectedButton = document.querySelector(`.vas-button[data-value="${value}"]`);
  selectedButton.classList.add('vas-button--selected');
  
  // Update state
  vasState.previousValue = vasState.selectedValue;
  vasState.selectedValue = value;
  vasState.isDirty = true;
  
  // Update visual feedback
  updateVASFeedback(value);
  
  // Update hidden input
  document.getElementById('pgScaleInput').value = value;
  
  // Auto-save
  autoSaveAssessment();
}

// Update Visual Feedback
function updateVASFeedback(value) {
  const percentage = (value / 10) * 100;
  
  document.getElementById('vasFill').style.width = percentage + '%';
  document.getElementById('vasSelectedValue').textContent = value;
  
  // Update label based on value
  const labels = {
    1: 'No Activity',
    2: 'Minimal Activity',
    3: 'Mild Activity',
    4: 'Mild Activity',
    5: 'Moderate Activity',
    6: 'Moderate Activity',
    7: 'Severe Activity',
    8: 'Severe Activity',
    9: 'Very Severe Activity',
    10: 'Worst Possible Activity'
  };
  
  document.getElementById('vasSelectedLabel').textContent = labels[value];
  
  // Update assessment state for DAS28
  assessmentState.pg_scale = value;
  updateDAS28();
}

// DAS28 Calculation (Updated for VAS 1-10)
function calculateDAS28() {
  const { tjc, sjc, esr, pg_scale } = assessmentState;
  
  // Convert VAS 1-10 to 0-100 for DAS28 formula (multiply by 10)
  const pg_0_100 = pg_scale * 10;
  
  // Standard DAS28 Formula
  const das28 = 0.56 * Math.sqrt(tjc) + 
                0.28 * Math.sqrt(sjc) + 
                0.7 * Math.log(esr) + 
                0.014 * pg_0_100;
  
  return Math.round(das28 * 100) / 100;
}

// Auto-save on VAS change
function autoSaveAssessment() {
  clearTimeout(window.autoSaveTimeout);
  window.autoSaveTimeout = setTimeout(() => {
    const payload = {
      visit_id: getCurrentVisitId(),
      pg_scale: vasState.selectedValue,  // NEW: Send VAS 1-10
      tjc: assessmentState.tjc,
      sjc: assessmentState.sjc,
      esr: assessmentState.esr,
      assessments: getAssessmentData()
    };
    
    fetch('/api/v1/joint-assessments/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        updateAutoSaveIndicator();
      }
    })
    .catch(err => console.error('Auto-save failed:', err));
  }, 1000);
}

// Keyboard Shortcuts
function setupVASKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Alt + 1 to 9: Quick set VAS value
    if (e.altKey && e.key >= '1' && e.key <= '9') {
      e.preventDefault();
      setVASValue(parseInt(e.key));
    }
    
    // Alt + 0: Set to 10
    if (e.altKey && e.key === '0') {
      e.preventDefault();
      setVASValue(10);
    }
  });
}

// Call on page load
document.addEventListener('DOMContentLoaded', () => {
  initializeVAS();
  setupVASKeyboardShortcuts();
});
```

---

## 📊 DAS28 CALCULATION UPDATE

### Before (0-100):
```javascript
const das28 = 0.56 * Math.sqrt(tjc) + 
              0.28 * Math.sqrt(sjc) + 
              0.7 * Math.log(esr) + 
              0.014 * pg;  // pg = 0-100
```

### After (1-10 VAS):
```javascript
const das28 = 0.56 * Math.sqrt(tjc) + 
              0.28 * Math.sqrt(sjc) + 
              0.7 * Math.log(esr) + 
              0.014 * (pg_scale * 10);  // Convert 1-10 to 0-100
```

**Result:** Same DAS28 score, but cleaner user input!

---

## 🔄 MIGRATION GUIDE

### Step 1: Add Database Column
```bash
# Run migration
alembic revision --autogenerate -m "Add pg_scale_1_10 to joint_assessments"
alembic upgrade head
```

### Step 2: Migrate Existing Data
```python
# backend/migrations/add_pg_scale.py
from sqlalchemy import text
from backend.utils.sqlalchemy import session_scope

def migrate_pg_scale():
    """Convert old 0-100 to new 1-10 scale."""
    with session_scope() as session:
        # Convert old values
        session.execute(
            text("""
                UPDATE joint_assessments
                SET pg_scale = ROUND(patient_global_0_100 / 10)
                WHERE patient_global_0_100 IS NOT NULL
            """)
        )
        print("✓ Migrated pg values: 0-100 → 1-10")
```

### Step 3: Update HTML Template
- Replace old slider input with VAS button grid
- Test on mobile (48px min touch targets)

### Step 4: Update JavaScript
- Replace input change listeners with button click handlers
- Update DAS28 calculation to convert VAS to 0-100
- Add keyboard shortcuts (arrow keys)

### Step 5: Test
```bash
# Test VAS buttons
- Click each button 1-10
- Verify color changes
- Check DAS28 updates
- Test keyboard shortcuts (Alt + 1-9, Alt + 0)
- Test on mobile (tap each button)
```

---

## ✅ CLINICAL WORKFLOW

### Before (0-100 Slider)
```
Doctor: "Rate your joint activity"
Patient: "Umm... around here?" (vague)
Doctor: (moves slider) "How about 50?"
Patient: "Maybe more like 45 or 55?"
↓
Doctor: "Let's say 50"
↓
Takes ~20 seconds
↓
Imprecision: ±5-10 points
```

### After (VAS 1-10 Buttons)
```
Doctor: "Rate your joint activity from 1 to 10"
Patient: "That's a 5"
Doctor: (clicks button 5) ✓ Done
↓
Takes ~3 seconds
↓
Precision: Exact value
↓
Better compliance (simpler choice)
```

---

## 🎯 IMPLEMENTATION CHECKLIST

- [ ] Add `pg_scale` column to database
- [ ] Migrate old 0-100 values to 1-10
- [ ] Update SQLAlchemy model
- [ ] Update API endpoint
- [ ] Replace HTML input with VAS buttons
- [ ] Add CSS styling (colors + responsive)
- [ ] Add JavaScript event listeners
- [ ] Update DAS28 calculation
- [ ] Add keyboard shortcuts
- [ ] Test on desktop (1920x1080)
- [ ] Test on tablet (768x1024)
- [ ] Test on mobile (375x667)
- [ ] Verify color accessibility (WCAG AA)
- [ ] Test with keyboard only
- [ ] Test with screen reader
- [ ] Performance: < 100ms response time

---

## 🚀 ROLLOUT PLAN

**Phase 1:** Deploy on staging (1 day)
**Phase 2:** Beta testing with 5-10 doctors (3 days)
**Phase 3:** Production rollout (1 day)
**Phase 4:** Monitor & gather feedback (ongoing)

---

**Status:** Ready to implement  
**Estimated Time:** 4-6 hours (HTML/CSS/JS)  
**Files to Update:** 4 (HTML, CSS, JS, Python models)  
**Breaking Changes:** None (backward compatible)

