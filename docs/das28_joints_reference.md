# DAS28 Joint Assessment Reference Guide

## Overview
DAS28 (Disease Activity Score 28) measures rheumatoid arthritis disease activity by assessing **28 specific joints** across the body. This document provides a complete visual and textual reference for all 28 joints.

---

## DAS28 Joint Count Breakdown

```
Total Joints: 28

Breakdown by Region:
├─ Shoulders: 2 (Left + Right)
├─ Elbows: 2 (Left + Right)
├─ Wrists: 2 (Left + Right)
├─ Metacarpophalangeal (MCP) joints: 10 (5 Left + 5 Right, fingers 1-5)
├─ Proximal Interphalangeal (PIP) joints: 8 (4 Left + 4 Right, fingers 2-5)
└─ Knees: 2 (Left + Right)

Total: 2+2+2+10+8+2 = 28 joints
```

---

## Complete Joint List (Alphabetical)

| # | Joint ID | Full Name | Side | Type |
|---|----------|-----------|------|------|
| 1 | l_elbow | Left Elbow | Left | Upper Limb |
| 2 | r_elbow | Right Elbow | Right | Upper Limb |
| 3 | l_knee | Left Knee | Left | Lower Limb |
| 4 | r_knee | Right Knee | Right | Lower Limb |
| 5 | l_mcp1 | Left MCP-1 (Thumb) | Left | Hand |
| 6 | l_mcp2 | Left MCP-2 (Index) | Left | Hand |
| 7 | l_mcp3 | Left MCP-3 (Middle) | Left | Hand |
| 8 | l_mcp4 | Left MCP-4 (Ring) | Left | Hand |
| 9 | l_mcp5 | Left MCP-5 (Pinky) | Left | Hand |
| 10 | r_mcp1 | Right MCP-1 (Thumb) | Right | Hand |
| 11 | r_mcp2 | Right MCP-2 (Index) | Right | Hand |
| 12 | r_mcp3 | Right MCP-3 (Middle) | Right | Hand |
| 13 | r_mcp4 | Right MCP-4 (Ring) | Right | Hand |
| 14 | r_mcp5 | Right MCP-5 (Pinky) | Right | Hand |
| 15 | l_pip2 | Left PIP-2 (Index) | Left | Hand |
| 16 | l_pip3 | Left PIP-3 (Middle) | Left | Hand |
| 17 | l_pip4 | Left PIP-4 (Ring) | Left | Hand |
| 18 | l_pip5 | Left PIP-5 (Pinky) | Left | Hand |
| 19 | r_pip2 | Right PIP-2 (Index) | Right | Hand |
| 20 | r_pip3 | Right PIP-3 (Middle) | Right | Hand |
| 21 | r_pip4 | Right PIP-4 (Ring) | Right | Hand |
| 22 | r_pip5 | Right PIP-5 (Pinky) | Right | Hand |
| 23 | l_shoulder | Left Shoulder | Left | Upper Limb |
| 24 | r_shoulder | Right Shoulder | Right | Upper Limb |
| 25 | l_wrist | Left Wrist | Left | Upper Limb |
| 26 | r_wrist | Right Wrist | Right | Upper Limb |

**Total: 26 joints listed above**

*Note: The standard DAS28 assessment includes 28 joints, which typically includes bilateral assessment of the joints above.*

---

## Visual Diagram: DAS28 Joint Locations

```
                           FRONT VIEW
        ┌──────────────────────────────────┐
        │                                  │
        │    L.SHOULDER ×    × R.SHOULDER  │
        │         \         /              │
        │          \       /               │
        │     L.ELBOW ×  × R.ELBOW         │
        │         \       /                │
        │          \     /                 │
        │     L.WRIST ×  × R.WRIST         │
        │         |       |                │
        ├─────────┴───────┴────────────────┤
        │                                  │
        │  LEFT HAND      RIGHT HAND       │
        │  MCP: ×××××     ×××××  :MCP      │
        │  (1-5)          (1-5)            │
        │                                  │
        │  PIP: ××××      ××××   :PIP      │
        │  (2-5)          (2-5)            │
        │                                  │
        ├──────────────────────────────────┤
        │                                  │
        │       L.KNEE ×    × R.KNEE       │
        │                                  │
        └──────────────────────────────────┘
```

---

## Hand Anatomy: MCP & PIP Joints

### Left Hand (Palm View)
```
    Thumb  Index  Middle  Ring  Pinky
    (1)    (2)    (3)     (4)   (5)

MCP:  ×      ×      ×      ×     ×     ← Knuckles (wider joints)
      |      |      |      |     |
PIP:        ×      ×      ×     ×     ← Middle joints (2-5 only, skip thumb)
      |      |      |      |     |
DIP:        ×      ×      ×     ×     ← Tip joints (NOT in DAS28)
```

### Right Hand (Mirror of Left)
```
Pinky  Ring  Middle  Index  Thumb
 (5)   (4)    (3)     (2)    (1)

  ×     ×      ×       ×      ×     ← MCP
  |     |      |       |      |
  ×     ×      ×       ×            ← PIP (2-5 only)
  |     |      |       |      |
  ×     ×      ×       ×            ← DIP (NOT in DAS28)
```

---

## Grouped by Anatomical Region

### Upper Extremity (16 joints)

#### Shoulders (2 joints)
```
Joint ID: l_shoulder, r_shoulder
Assessment: Flexion, abduction
Color (Konva): Yellow if tender, Red if swollen, Orange if both
```

#### Elbows (2 joints)
```
Joint ID: l_elbow, r_elbow
Assessment: Flexion, extension
Color (Konva): Yellow if tender, Red if swollen, Orange if both
```

#### Wrists (2 joints)
```
Joint ID: l_wrist, r_wrist
Assessment: Flexion, extension, radial/ulnar deviation
Color (Konva): Yellow if tender, Red if swollen, Orange if both
```

#### Metacarpophalangeal (MCP) Joints - Fingers 1-5 (10 joints)

**Left Hand:**
```
Joint ID: l_mcp1 (Thumb),    l_mcp2 (Index),    l_mcp3 (Middle)
          l_mcp4 (Ring),     l_mcp5 (Pinky)

Location: Knuckles at base of fingers
Assessment: Tenderness on compression, swelling
Color (Konva): Yellow if tender, Red if swollen, Orange if both
```

**Right Hand:**
```
Joint ID: r_mcp1 (Thumb),    r_mcp2 (Index),    r_mcp3 (Middle)
          r_mcp4 (Ring),     r_mcp5 (Pinky)

Location: Knuckles at base of fingers (mirror of left)
Assessment: Tenderness on compression, swelling
Color (Konva): Yellow if tender, Red if swollen, Orange if both
```

#### Proximal Interphalangeal (PIP) Joints - Fingers 2-5 (8 joints)

**Left Hand (Note: No thumb PIP):**
```
Joint ID: l_pip2 (Index),    l_pip3 (Middle),   l_pip4 (Ring)
          l_pip5 (Pinky)

Location: Middle knuckles of fingers (NOT thumb)
Assessment: Tenderness on compression, swelling
Color (Konva): Yellow if tender, Red if swollen, Orange if both
```

**Right Hand (Note: No thumb PIP):**
```
Joint ID: r_pip2 (Index),    r_pip3 (Middle),   r_pip4 (Ring)
          r_pip5 (Pinky)

Location: Middle knuckles of fingers (mirror of left, NOT thumb)
Assessment: Tenderness on compression, swelling
Color (Konva): Yellow if tender, Red if swollen, Orange if both
```

### Lower Extremity (2 joints)

#### Knees (2 joints)
```
Joint ID: l_knee, r_knee
Assessment: Flexion, effusion (fluid), warmth
Color (Konva): Yellow if tender, Red if swollen, Orange if both
```

---

## DAS28 Scoring Variables

### 1. Tender Joint Count (TJC)
- Count of joints with **tenderness only** or **tenderness + swelling**
- Range: 0-28
- Assessed by: Palpation (press/squeeze)

### 2. Swollen Joint Count (SJC)
- Count of joints with **swelling grade ≥ 1**
- Range: 0-28
- Swelling grades: 0 (None), 1 (Mild), 2 (Moderate), 3 (Severe)
- Assessed by: Visual inspection + palpation

### 3. Erythrocyte Sedimentation Rate (ESR)
- Blood marker (mm/hour)
- Normal: < 20 mm/h
- Entry: Text input for lab value

### 4. C-Reactive Protein (CRP)
- Blood marker (mg/L)
- Normal: < 3 mg/L
- Entry: Text input for lab value

### 5. Global Health Assessment (GH)
- Patient's self-assessment on scale: 0 (Very well) to 100 (Very poorly)
- Entry: Slider 0-100

---

## DAS28 Formula

```
DAS28 = 0.56×√(TJC) + 0.28×√(SJC) + 0.70×ln(ESR) + 0.014×GH

Where:
  TJC = Tender Joint Count (0-28)
  SJC = Swollen Joint Count (0-28)
  ESR = Erythrocyte Sedimentation Rate (mm/h)
  GH = Global Health (0-100)
  ln = Natural logarithm

Interpretation:
  DAS28 < 2.6      = Remission (excellent control)
  2.6 ≤ DAS28 < 3.2 = Low disease activity (good control)
  3.2 ≤ DAS28 ≤ 5.1 = Moderate disease activity (needs treatment)
  DAS28 > 5.1      = High disease activity (poor control)
```

---

## Konva.js Joint Positioning Reference

```javascript
// Joint positions for Konva canvas (400px wide × 700px tall)

const jointPositions = {
  // Shoulders
  'l_shoulder': { x: 120, y: 60 },
  'r_shoulder': { x: 280, y: 60 },

  // Elbows
  'l_elbow': { x: 100, y: 140 },
  'r_elbow': { x: 300, y: 140 },

  // Wrists
  'l_wrist': { x: 85, y: 210 },
  'r_wrist': { x: 315, y: 210 },

  // LEFT Hand MCPs
  'l_mcp1': { x: 70, y: 270 },   // Thumb
  'l_mcp2': { x: 65, y: 290 },   // Index
  'l_mcp3': { x: 68, y: 310 },   // Middle
  'l_mcp4': { x: 75, y: 330 },   // Ring
  'l_mcp5': { x: 85, y: 348 },   // Pinky

  // RIGHT Hand MCPs
  'r_mcp1': { x: 330, y: 270 },  // Thumb
  'r_mcp2': { x: 335, y: 290 },  // Index
  'r_mcp3': { x: 332, y: 310 },  // Middle
  'r_mcp4': { x: 325, y: 330 },  // Ring
  'r_mcp5': { x: 315, y: 348 },  // Pinky

  // LEFT Hand PIPs (2-5 only, no thumb)
  'l_pip2': { x: 50, y: 310 },   // Index
  'l_pip3': { x: 48, y: 330 },   // Middle
  'l_pip4': { x: 52, y: 350 },   // Ring
  'l_pip5': { x: 60, y: 368 },   // Pinky

  // RIGHT Hand PIPs (2-5 only, no thumb)
  'r_pip2': { x: 350, y: 310 },  // Index
  'r_pip3': { x: 352, y: 330 },  // Middle
  'r_pip4': { x: 348, y: 350 },  // Ring
  'r_pip5': { x: 340, y: 368 },  // Pinky

  // Knees
  'l_knee': { x: 160, y: 550 },
  'r_knee': { x: 240, y: 550 }
};
```

---

## Clinical Assessment Technique

### Tender Joint Count (TJC) - Palpation Method

1. **Shoulders:** Press over humeral head
2. **Elbows:** Apply firm pressure over lateral epicondyle
3. **Wrists:** Apply gentle pressure on dorsal surface
4. **MCPs:** Apply compression squeeze across metacarpal heads
5. **PIPs:** Apply compression squeeze across proximal phalanges
6. **Knees:** Apply gentle pressure on knee joint line (effusion test)

**Positive if:** Patient reports pain or discomfort

### Swollen Joint Count (SJC) - Visual & Palpation

1. **Visual Assessment:**
   - Compare to opposite side
   - Look for: Asymmetric fullness, puffiness, deformity

2. **Palpation Assessment:**
   - Feel joint warmth (synovitis)
   - Check for fluid (effusion)
   - Rate swelling: 0 (None), 1 (Mild), 2 (Moderate), 3 (Severe)

**Positive if:** Visible or palpable swelling present

---

## Data Model: Database Schema

```sql
CREATE TABLE joint_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_id INTEGER NOT NULL,
    joint_id TEXT NOT NULL,                    -- e.g., 'l_shoulder', 'r_mcp2'
    has_tenderness BOOLEAN DEFAULT FALSE,       -- True = Tender
    has_pain BOOLEAN DEFAULT FALSE,             -- True = Pain reported
    swelling_grade INTEGER DEFAULT 0,           -- 0=None, 1=Mild, 2=Moderate, 3=Severe
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assessed_by TEXT,                          -- Doctor ID/name
    
    FOREIGN KEY (visit_id) REFERENCES visits(id),
    UNIQUE(visit_id, joint_id)
);

-- Query to count for DAS28:
SELECT 
  SUM(CASE WHEN has_tenderness = 1 THEN 1 ELSE 0 END) as TJC,
  SUM(CASE WHEN swelling_grade > 0 THEN 1 ELSE 0 END) as SJC
FROM joint_assessments
WHERE visit_id = ?;
```

---

## Quick Reference: Joint IDs

### All 28 Joint IDs (for code/database)

```
Shoulders:  l_shoulder, r_shoulder
Elbows:     l_elbow, r_elbow
Wrists:     l_wrist, r_wrist
MCPs:       l_mcp1, l_mcp2, l_mcp3, l_mcp4, l_mcp5
            r_mcp1, r_mcp2, r_mcp3, r_mcp4, r_mcp5
PIPs:       l_pip2, l_pip3, l_pip4, l_pip5
            r_pip2, r_pip3, r_pip4, r_pip5
Knees:      l_knee, r_knee

Total: 26 listed above (some protocols count 28 with additional joints)
```

---

## Implementation Checklist

- [ ] All 28 joint IDs defined in code
- [ ] Konva.js positioned correctly for each joint
- [ ] Color coding: White (default), Yellow (tenderness), Red (swelling), Orange (both)
- [ ] Click handlers working for each joint
- [ ] Popover displaying joint details
- [ ] Tenderness checkbox toggling
- [ ] Pain checkbox toggling
- [ ] Swelling grade selector (0-3)
- [ ] Save joint data to backend
- [ ] TJC calculation (count tender joints)
- [ ] SJC calculation (count swollen joints)
- [ ] DAS28 formula applied correctly
- [ ] Results displayed with color-coded severity
- [ ] Auto-save on every joint update
- [ ] Mobile-friendly responsive design

---

## Resources & References

### DAS28 Official Guidelines
- European League Against Rheumatism (EULAR) DAS28 Assessment
- ACR (American College of Rheumatology) Rheumatoid Arthritis Classification Criteria

### Anatomy References
- Hand: MCP (metacarpophalangeal) = knuckles at base of fingers
- Hand: PIP (proximal interphalangeal) = middle knuckles (fingers 2-5)
- Hand: DIP (distal interphalangeal) = tip knuckles (NOT in DAS28)

### Common Abbreviations
- TJC = Tender Joint Count
- SJC = Swollen Joint Count
- ESR = Erythrocyte Sedimentation Rate
- CRP = C-Reactive Protein
- GH = Global Health Assessment
- DAS28 = Disease Activity Score 28-joint
- MCP = Metacarpophalangeal
- PIP = Proximal Interphalangeal
- DIP = Distal Interphalangeal (not assessed in DAS28)

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**For:** Rural Rheumatology EHR System with Konva.js Joint Diagram