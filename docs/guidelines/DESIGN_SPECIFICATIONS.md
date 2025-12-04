# Design Specifications - Rheumatology EHR for Rural Clinics

## Project Overview

**Application Name**: Rheumatology EHR
**Target Users**: Rheumatology doctors, clinicians, nurses, hospital administrators in rural India and low-resource countries
**Primary Goal**: Fast, accessible, offline-capable electronic health record system
**Performance Target**: <150KB total bundle size, <1 second load on 3G
**Platform Support**: Windows 7, IE11+, 10+ year old computers

## Core Features
*   **Patient Management**: CRUD operations for patient data.
*   **Visit Tracking**: History of patient visits.
*   **Medical Notes**: Auto-save and offline voice recognition (VOSK).
*   **DAS28 Automation**: Automatic calculation of disease activity score.
*   **Joint Assessment**: 3-parameter (Tenderness, Pain, Swelling) visual assessment.

## Frontend Stack
*   **HTMX** (14KB): Server-driven UI updates.
*   **Pico.css** (11.3KB): Minimal CSS framework.
*   **Konva.js** (80KB): Canvas library for Joint Diagrams.
*   **Alpine.js** (15KB): Lightweight JavaScript framework for state.
*   **VOSK** (50MB): Offline speech recognition model.

---

## Design Philosophy

### Core Principles

1. **Speed > Beauty**: Performance is the top priority
2. **Accessibility > Aesthetics**: WCAG AAA compliance (7:1 contrast)
3. **Simplicity > Complexity**: Minimal, functional design
4. **Doctor-friendly > Designer-friendly**: Built for clinical workflows
5. **Offline-first**: Works without internet connection

### Constraints

❌ **Not Allowed**:
- Web fonts (use system fonts only)
- Animations or transitions
- Complex visual effects
- Libraries that increase bundle size significantly
- Features requiring constant internet connection

✅ **Required**:
- System fonts
- High contrast (7:1 minimum)
- 48px minimum button height
- Keyboard accessibility
- Offline functionality
- Auto-save (every 30 seconds)

---

## Color System

### Core Colors

| Color Name | Hex Code | Usage | Contrast Ratio |
|------------|----------|-------|----------------|
| Primary Blue | `#0066CC` | Primary actions, branding, links | 7.0:1 on white |
| Draft Orange | `#FF9900` | Draft status, warning states | 3.8:1 on white |
| Success Green | `#00AA00` | Success states, finalized notes | 7.5:1 on white |
| Error Red | `#CC0000` | Error states, required fields | 8.2:1 on white |

### DAS28 Disease Activity Colors

| Score Range | Color | Hex Code | Label |
|-------------|-------|----------|-------|
| < 2.6 | Green | `#00AA00` | Remission |
| 2.6 - 3.2 | Yellow | `#FFCC00` | Low Activity |
| 3.2 - 5.1 | Orange | `#FF9900` | Moderate Activity |
| > 5.1 | Red | `#CC0000` | High Activity |

### Neutral Colors

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Text Primary | `#000000` | Main text (21:1 on white) |
| Text Secondary | `#333333` | Helper text, labels (12.6:1 on white) |
| Border | `#CCCCCC` | Borders, dividers |
| Hover/Muted | `#F5F5F5` | Hover states, backgrounds |
| Background | `#FFFFFF` | Page background |
| Disabled | `#999999` | Disabled text/elements |

### Auto-save Indicator Colors

| Status | Color | Hex Code |
|--------|-------|----------|
| Saving | Yellow | `#FFCC00` |
| Saved | Green | `#00AA00` |
| Error | Red | `#CC0000` |

---

## Typography

### Font Stack

```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
```

**Rationale**: System fonts load instantly, reduce bundle size, and provide native OS appearance.

### Font Sizes

| Size Name | Pixels | REM | Usage |
|-----------|--------|-----|-------|
| Extra Small | 12px | 0.75rem | Labels, captions |
| Small | 14px | 0.875rem | Helper text, secondary info |
| Base | 16px | 1rem | Body text, inputs |
| Large | 18px | 1.125rem | Headings (H3) |
| Extra Large | 24px | 1.5rem | Headings (H2) |
| 2XL | 32px | 2rem | Headings (H1) |

### Font Weights

- **Regular (400)**: Body text, inputs, helper text
- **Bold (600)**: Headings, labels, buttons

*Note: Only 400 and 600 weights are used to minimize font loading.*

### Line Height

- **Base**: 1.6 (for body text and inputs)
- **Tight**: 1.4 (for headings when needed)

**Rationale**: 1.6+ line-height improves readability, especially for medical documentation.

---

## Spacing System

### Scale

| Size | Pixels | Usage |
|------|--------|-------|
| XS | 4px | Tight spacing, internal padding |
| SM | 8px | Gap between related elements |
| MD | 16px | Standard spacing, card padding |
| LG | 24px | Section spacing |
| XL | 32px | Major section dividers |

### Application

- **Button padding**: 24px horizontal (6 × 4px)
- **Card padding**: 16px (MD)
- **Form field gaps**: 16px (MD)
- **Section spacing**: 24px (LG)
- **Page margins**: 16px mobile, 24px desktop

---

## Components

### Buttons

#### Specifications

| Property | Value |
|----------|-------|
| **Height (Default)** | 48px (minimum for touch targets) |
| **Height (Large)** | 56px |
| **Padding** | 24px horizontal, auto vertical |
| **Border** | 2px solid |
| **Border Radius** | 4px |
| **Font Weight** | 600 (Bold) |
| **Font Size** | 16px |

#### Variants

1. **Primary** - `#0066CC` background, white text
2. **Secondary** - White background, `#CCCCCC` border, black text
3. **Success** - `#00AA00` background, white text
4. **Draft** - `#FF9900` background, white text
5. **Error** - `#CC0000` background, white text
6. **Disabled** - `#CCCCCC` background, `#999999` text

#### States

- **Default**: Defined colors above
- **Hover**: Darker shade (e.g., `#004C99` for primary)
- **Focus**: 3px `#0066CC` outline with 2px offset
- **Disabled**: Gray with reduced opacity, cursor not-allowed

### Form Elements

#### Input Fields

| Property | Value |
|----------|-------|
| **Height** | 48px |
| **Padding** | 16px horizontal |
| **Border** | 2px solid `#CCCCCC` |
| **Border (Focus)** | 2px solid `#0066CC` |
| **Border (Error)** | 2px solid `#CC0000` |
| **Border Radius** | 4px |
| **Font Size** | 16px |
| **Background** | White |

#### Textarea

- Same as input, but variable height
- Minimum height: 128px (8 lines)
- Padding: 16px all sides

#### Select Dropdown

- Same styling as input field
- Height: 48px
- Arrow indicator included

#### Labels

- Font weight: 600 (Bold)
- Font size: 16px
- Margin bottom: 8px
- Color: Black `#000000`

#### Helper Text

- Font size: 14px
- Color: `#333333` (neutral) or `#CC0000` (error)
- Margin top: 8px

### Cards

| Property | Value |
|----------|-------|
| **Padding** | 16px |
| **Border** | 2px solid `#CCCCCC` |
| **Border Radius** | 4px |
| **Background** | White |
| **Hover** (if clickable) | `#F5F5F5` background |

#### Card Header

- Padding bottom: 16px
- Border bottom: 2px solid `#CCCCCC`
- Margin bottom: 16px

### Tables

| Element | Styling |
|---------|---------|
| **Border** | 2px solid `#CCCCCC` (outer) |
| **Header Row** | `#F5F5F5` background, 2px bottom border |
| **Cells** | 16px padding, 1px bottom border |
| **Hover Row** | `#F5F5F5` background (if clickable) |

### Modals

| Property | Value |
|----------|-------|
| **Overlay** | Black with 50% opacity |
| **Border** | 2px solid `#CCCCCC` |
| **Border Radius** | 4px |
| **Max Width (Small)** | 448px (28rem) |
| **Max Width (Medium)** | 672px (42rem) |
| **Max Width (Large)** | 896px (56rem) |
| **Max Height** | 90vh |
| **Padding** | 16px |

---

## Special Components

### Auto-save Indicator

**Visual Design**:
- Status dot: 12px circle
- Border: 2px solid `#CCCCCC`
- Padding: 8px horizontal, 4px vertical
- Background: White

**States**:
1. **Saving**: Yellow dot + "Saving..." text
2. **Saved**: Green dot + "Saved" text + timestamp
3. **Error**: Red dot + "Error - Not Saved" text

### DAS28 Score Display

**Visual Design**:
- Full-width colored bar
- Border: 2px matching color
- Border radius: 4px
- Padding: 12px horizontal
- Font size: 16px (label), 18px (score)

**Color Coding**:
- Green: Remission (<2.6)
- Yellow: Low Activity (2.6-3.2)
- Orange: Moderate Activity (3.2-5.1)
- Red: High Activity (>5.1)

### Joint Assessment Canvas

**Specifications**:
- Canvas size: 600px × 550px
- Joint radius: 20px
- Swelling halo: +5px per grade (up to 3)
- Tenderness marker: Red X (cross)
- Border: 2px solid `#CCCCCC`
- Background: White

**Interactions**:
- Left click: Cycle swelling (0→1→2→3→0)
- Right click: Toggle tenderness
- Visual feedback: Selected joint highlighted in blue

---

## Layout System

### Responsive Breakpoints

| Breakpoint | Width | Usage |
|------------|-------|-------|
| Mobile | < 768px | Single column, stacked layout |
| Tablet | 768px - 1024px | 2-column grids where appropriate |
| Desktop | > 1024px | Multi-column layouts, side-by-side |

### Grid System

- **Default**: Single column (mobile-first)
- **2-column**: Stats, form pairs (tablet+)
- **4-column**: Statistics cards (desktop)
- **Gap**: 16px (1rem)

### Container

- **Max width**: 1280px (80rem)
- **Padding**: 16px mobile, 24px desktop
- **Centered**: Margin auto

---

## Page Layouts

### 1. Dashboard

**Sections**:
1. Header with greeting
2. 4-column statistics grid
3. Quick actions card
4. Recent patients list
5. System status

### 2. Patient Management

**Sections**:
1. Search bar + Add Patient button
2. Results count
3. Patient table (7 columns)
4. Patient detail modal
5. Add patient modal

### 3. Medical Note

**Sections**:
1. Auto-save indicator (top right)
2. Patient info card
3. Chief complaint
4. History of present illness
5. Physical examination (with joint assessment link)
6. Assessment
7. Plan
8. Medications
9. Follow-up
10. Action buttons (Save Draft / Finalize)

### 4. Joint Assessment

**Sections**:
1. Patient info card
2. Interactive canvas
3. Joint count summary (tender/swollen)
4. Lab values (ESR, Patient Global)
5. DAS28 calculator
6. Reference information
7. Action buttons

### 5. Reports & Analytics

**Sections**:
1. Report filters (type, date range)
2. Summary statistics (4-column grid)
3. Recent visits table
4. Disease distribution bar charts
5. DAS28 distribution bar charts
6. Export options

### 6. Design System Documentation

**Sections**:
1. Color palette showcase
2. Typography examples
3. Button variants
4. Form elements
5. Special components
6. Accessibility standards
7. Performance optimizations
8. Design constraints

---

## Navigation

### Header

**Desktop**:
- Height: Auto (content-based)
- Horizontal tab navigation
- Sticky position
- Background: `#0066CC`
- Text: White
- Active state: Darker blue `#004C99`

**Mobile**:
- Hamburger menu icon
- Slide-in drawer navigation
- Overlay: Black 50% opacity
- Menu width: 256px

### Navigation Items

1. 📊 Dashboard
2. 👥 Patients
3. 📝 Medical Note
4. 🫴 Joint Assessment
5. 📈 Reports
6. 🎨 Design System

---

## Accessibility Features

### Focus Management

- **Outline**: 3px solid `#0066CC`
- **Offset**: 2px
- **Applied to**: All interactive elements

### Keyboard Navigation

- **Tab**: Navigate forward
- **Shift + Tab**: Navigate backward
- **Enter/Space**: Activate buttons
- **Escape**: Close modals
- **Arrow keys**: Navigate select options

### Screen Reader Support

- Semantic HTML structure
- ARIA labels on all interactive elements
- Proper heading hierarchy
- Form labels associated with inputs
- Alternative text for visual elements

### Touch Targets

- Minimum size: 48px × 48px
- Adequate spacing: 8px minimum
- Large variant: 56px height available

---

## Performance Optimizations

### Bundle Size

**Target**: <150KB total (including fonts, icons, etc.)

**Strategies**:
1. System fonts only (0KB font loading)
2. No animation libraries
3. Minimal CSS (Tailwind v4 with purging)
4. Canvas-based joint assessment (no heavy libraries)
5. No external dependencies where possible

### Load Time

**Target**: <1 second on 3G

**Strategies**:
1. Minimal JavaScript
2. No web fonts to download
3. Optimized images (if any)
4. Efficient CSS
5. Code splitting (if needed)

### Offline Support

- Service worker for caching
- Local storage for draft notes
- Auto-save functionality
- Clear offline indicators

---

## Browser Support

### Minimum Requirements

- **IE11+** (Windows 7)
- **Chrome 60+**
- **Firefox 60+**
- **Safari 11+**
- **Edge 79+**

### Progressive Enhancement

- Core functionality works in all browsers
- Enhanced features in modern browsers
- Graceful degradation for old browsers
- No breaking features in legacy environments

---

## File Structure

```
frontend/src/
├── App.jsx                          # Main application shell
├── components/                      # Shell UI components
│   ├── Sidebar.jsx
│   ├── Header.jsx
│   └── ...
├── pages/                           # Page shells (load HTMX fragments)
│   ├── Dashboard.jsx
│   ├── Patients.jsx
│   ├── MedicalNote.jsx
│   └── JointAssessment.jsx

backend/templates/fragments/         # Core Business Logic (HTMX + Alpine)
├── medical_note_form.html           # Medical Note Form & Logic
├── joint_assessment.html            # Joint Map Canvas & Logic
├── patients_list.html
└── ...
```

---

## Implementation Notes

### CSS Variables (in globals.css)

```css
:root {
  /* Colors */
  --color-primary: #0066CC;
  --color-draft: #FF9900;
  --color-success: #00AA00;
  --color-error: #CC0000;

  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.5rem;
  --text-2xl: 2rem;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Interactive */
  --button-height: 48px;
  --input-height: 48px;
  --border-radius: 4px;
  --border-width: 2px;
}
```

### Tailwind Usage

- Use utility classes for layout and spacing
- Avoid font-size/weight classes (use default typography)
- Use exact color values in square brackets: `bg-[#0066CC]`
- Responsive prefixes: `md:`, `lg:` for breakpoints

---

## Testing Requirements

### Visual Testing

- [ ] Test on Windows 7 with IE11
- [ ] Test on 10+ year old hardware
- [ ] Test at 100%, 125%, 150%, 200% zoom
- [ ] Test with high contrast mode
- [ ] Test on mobile devices

### Functional Testing

- [ ] Keyboard-only navigation
- [ ] Screen reader compatibility (NVDA, JAWS)
- [ ] Touch interactions on tablets
- [ ] Print functionality
- [ ] Offline mode

### Performance Testing

- [ ] Bundle size < 150KB
- [ ] Load time < 1s on 3G
- [ ] Auto-save every 30s
- [ ] Canvas performance on old hardware

---

## Future Considerations

### Potential Enhancements

1. **PWA Features**: Install as app, push notifications
2. **Data Sync**: Background sync when online
3. **Export Options**: PDF generation, CSV exports
4. **Localization**: Multiple languages (Hindi, etc.)
5. **Voice Input**: Speech-to-text for notes
6. **Barcode Scanning**: Patient ID scanning

### Scalability

- Modular component architecture
- Easy to add new pages/features
- Consistent design patterns
- Reusable components

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-15 | Initial design specifications |

---

## Contact & Support

For questions about design specifications:
- Review this document first
- Check ACCESSIBILITY_CHECKLIST.md
- Consult Design System page in application
- Contact development team for clarifications

---

**Document Status**: ✅ Complete
**Last Updated**: November 15, 2025
**Version**: 1.0
