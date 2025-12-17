# Modern Theme Components

## Overview

This document describes the modern UI components extracted from DaisyUI, FloatUI, and FlyonUI. These components are implemented as pure CSS/SCSS without any plugin dependencies, keeping the bundle lightweight.

**Implementation Date**: December 2024
**Bundle Impact**: +8 KB uncompressed (+0 KB gzipped)
**Source File**: `backend/static/scss/_extracted-components.scss`

---

## Bundle Size Budget

| Metric | Value | Status |
|--------|-------|--------|
| Target (gzipped) | 150 KB | Within budget |
| Current (gzipped) | ~106 KB | 71% used |
| CSS Addition | +8 KB | Minimal impact |
| Headroom | 44 KB | Available for future |

---

## Component Reference

### 1. Stats/KPI Component

**Source**: DaisyUI
**Size**: ~1.2 KB
**Usage**: Dashboard metrics display

```html
<article class="stat glass">
  <div class="stat-title">Patients Today</div>
  <div class="stat-value">127</div>
  <div class="stat-desc stat-desc-success">↑ 12 from yesterday</div>
</article>
```

**Classes**:
- `.stat` - Base stat container (grid layout)
- `.stat-title` - Uppercase label
- `.stat-value` - Large number display (2.25rem, 800 weight)
- `.stat-desc` - Description text
- `.stat-desc-success` / `.stat-desc-warning` / `.stat-desc-error` - Colored descriptions

**Grid Layout**:
```html
<div class="stats">
  <article class="stat glass">...</article>
  <article class="stat glass">...</article>
</div>
```

---

### 2. Glass Card

**Source**: FloatUI
**Size**: ~0.8 KB
**Usage**: Modern frosted glass effect for cards

```html
<div class="glass">
  <!-- Card content -->
</div>

<!-- With hover effect -->
<div class="glass glass-hover">
  <!-- Card content -->
</div>
```

**CSS Properties**:
- `background: rgba(255, 255, 255, 0.7)`
- `backdrop-filter: blur(12px)`
- `border: 1px solid rgba(255, 255, 255, 0.3)`
- `box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08)`

**Dark Mode**: Automatically adjusts to `[data-theme="dark"]`

---

### 3. Toast Notifications

**Source**: DaisyUI
**Size**: ~1.0 KB
**Usage**: Non-blocking save status alerts

```html
<!-- Container in base.html -->
<div class="toast-container" id="toast-container" x-data="toastManager()">
  <!-- Toasts render here -->
</div>
```

**JavaScript API**:
```javascript
// Show toast (auto-dismisses after duration)
window.showToast('Changes saved', 'success', 3000);
window.showToast('Error occurred', 'error', 5000);
window.showToast('Processing...', 'info', 0); // 0 = no auto-dismiss
```

**Alert Types**:
- `.alert-success` - Green, checkmark icon
- `.alert-error` - Red, X icon
- `.alert-warning` - Amber, warning icon
- `.alert-info` - Blue, info icon

**Animation**: Slides in from right, slides out on dismiss

---

### 4. Modern Badges

**Source**: DaisyUI
**Size**: ~0.6 KB
**Usage**: DAS28 severity indicators, status labels

```html
<span class="badge-modern badge-success">Remission</span>
<span class="badge-modern badge-warning">Low Activity</span>
<span class="badge-modern badge-info">Moderate</span>
<span class="badge-modern badge-error">High Activity</span>
<span class="badge-modern badge-neutral">Inactive</span>
```

**With Dot Indicator**:
```html
<span class="badge-modern badge-lg badge-success">
  <span class="badge-dot"></span> Remission
</span>
```

**Variants**:
- `.badge-lg` - Larger padding and font size
- `.badge-dot` - Circular indicator inside badge

---

### 5. Skeleton Loaders

**Source**: DaisyUI
**Size**: ~0.5 KB
**Usage**: Loading states for async content

```html
<!-- Generic skeleton -->
<div class="skeleton" style="width: 100px; height: 20px;"></div>

<!-- Pre-styled variants -->
<div class="skeleton-text"></div>
<div class="skeleton-title"></div>
<div class="skeleton-avatar"></div>
<div class="skeleton-card"></div>
```

**Animation**: Pulsing gradient shimmer effect

---

### 6. Button Variants

**Source**: FlyonUI
**Size**: ~0.9 KB
**Usage**: Enhanced button styles

```html
<!-- Ghost button (transparent) -->
<button class="btn-ghost">Cancel</button>

<!-- Outline button -->
<button class="btn-outline">Edit</button>

<!-- Loading state (add to any button) -->
<button class="btn-loading">Saving...</button>
```

**Button Group**:
```html
<div class="btn-group">
  <button>Left</button>
  <button>Center</button>
  <button>Right</button>
</div>
```

---

### 7. Tabs (Boxed)

**Source**: DaisyUI
**Size**: ~0.8 KB
**Usage**: Tab navigation

```html
<div class="tabs-boxed">
  <button class="tab tab-active">Tab 1</button>
  <button class="tab">Tab 2</button>
  <button class="tab">Tab 3</button>
</div>

<!-- Full width variant -->
<div class="tabs-boxed tabs-full">
  <button class="tab tab-active">Tab 1</button>
  <button class="tab">Tab 2</button>
</div>
```

**States**:
- Default: Muted text, transparent background
- Hover: Light background
- Active (`.tab-active`): White background, primary color text, shadow

---

### 8. Timeline

**Source**: FloatUI
**Size**: ~1.0 KB
**Usage**: Visit history visualization

```html
<div class="timeline">
  <div class="timeline-item timeline-success">
    <div class="timeline-title">Joint Assessment</div>
    <div class="timeline-time">Dec 15, 2024</div>
    <div class="timeline-content">DAS28-ESR: 2.4 (Remission)</div>
  </div>
  <div class="timeline-item timeline-warning">
    <div class="timeline-title">Follow-up Visit</div>
    <div class="timeline-time">Nov 20, 2024</div>
    <div class="timeline-content">Medication adjusted</div>
  </div>
</div>

<!-- Compact variant -->
<div class="timeline-compact">
  ...
</div>
```

**Status Variants** (dot color):
- `.timeline-success` - Green
- `.timeline-warning` - Amber
- `.timeline-error` - Red
- `.timeline-info` - Blue

---

## Utility Classes

### Text Colors
```html
<span class="text-success">Success text</span>
<span class="text-warning">Warning text</span>
<span class="text-error">Error text</span>
<span class="text-info">Info text</span>
```

### Background Colors
```html
<div class="bg-success-subtle">Light green background</div>
<div class="bg-warning-subtle">Light amber background</div>
<div class="bg-error-subtle">Light red background</div>
<div class="bg-info-subtle">Light blue background</div>
```

### Divider
```html
<div class="divider">OR</div>
```

### Card Hover Effect
```html
<div class="card-hover">
  <!-- Lifts on hover with shadow -->
</div>
```

---

## CSS Custom Properties

These variables are defined in `custom-theme.scss` and can be used in custom styles:

```scss
:root {
  // Healthcare Blue Palette
  --color-primary: #2563eb;
  --color-primary-light: #3b82f6;
  --color-primary-dark: #1d4ed8;

  // Semantic Colors
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;
  --color-info: #0ea5e9;

  // Surface Colors
  --color-surface: #ffffff;
  --color-surface-alt: #f8fafc;
  --color-border: #e2e8f0;
}
```

---

## Dark Mode Support

Components automatically adapt to dark mode when `[data-theme="dark"]` is set on `<html>`:

```html
<html data-theme="dark">
```

Supported components:
- Glass cards (darker background)
- Badges (adjusted colors)
- Tabs (darker background)
- All text/background utilities

---

## Accessibility

| Component | WCAG Level | Notes |
|-----------|------------|-------|
| Stats | AA | High contrast values |
| Glass Card | AA | 70% opacity ensures readability |
| Toast | AAA | 4.5:1 contrast, auto-dismiss |
| Badges | AA | Color + text label |
| Skeleton | N/A | Decorative only |
| Buttons | AAA | 48px touch targets maintained |
| Tabs | AA | Focus visible, keyboard nav |
| Timeline | AA | Sufficient contrast |

---

## Integration with Alpine.js

The toast system integrates with Alpine.js via a global component:

```javascript
// Registered in base.html
Alpine.data('toastManager', () => ({
  toasts: [],
  addToast(message, type, duration) { ... },
  removeToast(id) { ... },
  getIcon(type) { ... }
}));

// Global helper function
window.showToast(message, type, duration);
```

---

## Files Modified

| File | Changes |
|------|---------|
| `backend/static/scss/_extracted-components.scss` | New file with all components |
| `backend/static/scss/custom-theme.scss` | Healthcare colors + import |
| `backend/templates/base.html` | Toast container + Alpine component |
| `backend/templates/dashboard.html` | Stats, glass cards, badges |
| `backend/templates/medical_note.html` | Toast notifications |
| `backend/templates/fragments/joint_assessment.html` | Badges, glass card |

---

## Future Considerations

1. **Additional Components**: Timeline is available but not yet used in templates
2. **Dark Mode Toggle**: Can be added to navbar when needed
3. **More Skeletons**: Can add page-specific skeleton layouts
4. **Animation Control**: Animations use `prefers-reduced-motion` media query
