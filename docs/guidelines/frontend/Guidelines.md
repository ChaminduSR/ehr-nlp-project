# Frontend Development Guidelines

These guidelines are derived from `DESIGN_SPECIFICATIONS.md` and `ACCESSIBILITY_CHECKLIST.md`. All frontend code must adhere to these rules.

## 1. Core Principles & Constraints
*   **Performance First**: Target <150KB total bundle size. Load time <1 second on 3G.
*   **Browser Support**: **Modern Browsers Only** (Chrome, Firefox, Edge). **IE11 is NOT supported**.
*   **Offline-First**: The app must function without an internet connection (Service Workers, LocalStorage).
*   **Accessibility**: WCAG AAA Compliance is mandatory.
*   **Core Features**:
    *   Patient management
    *   Visit tracking
    *   Medical notes (auto-save + voice)
    *   DAS28 automation
    *   Joint assessment (3-parameter)

## 2. Design & Styling
*   **Framework**: **Pico.css** (Semantic HTML) + **Tailwind CSS** (Utility).
*   **Fonts**: Use **System Fonts ONLY**. No web fonts (Google Fonts, etc.).
    *   `font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;`
*   **Animations**: **NO animations** or transitions, except for essential UI feedback (e.g., hover states).
*   **Colors**:
    *   Primary: `#0066CC`
    *   Success: `#00AA00`
    *   Error: `#CC0000`
    *   Text: `#000000` (Primary), `#333333` (Secondary)
*   **Contrast**: Minimum **7:1** contrast ratio for all text and interactive elements.
*   **Touch Targets**: Minimum **48px** height for all interactive elements (buttons, inputs).

## 3. Coding Standards
*   **Language**: **TypeScript** (Strict Mode).
*   **Frameworks**:
    *   **React 19**: For complex interactive components (Patient List, etc.).
    *   **Alpine.js**: For lightweight interactivity in server-rendered templates.
    *   **HTMX**: For server-driven UI updates.
*   **State Management**:
    *   **TanStack Query**: For server state (React).
    *   **Alpine.js `x-data`**: For local UI state.
*   **Validation**: **Zod** for schema validation.
*   **HTML**: Use semantic HTML5.
    *   Always provide `alt` text for images.
    *   Always provide `aria-label` for icon-only buttons.
*   **Frontend Integration**:
    *   **HTMX**: Use `hx-get`, `hx-post` for server interactions.
    *   **Konva.js**: Use for the Joint Assessment canvas.
    *   **VOSK**: Use for offline speech recognition.

## 4. Accessibility Checklist (Quick Reference)
*   [ ] All inputs have associated labels.
*   [ ] Focus indicators are visible (3px solid `#0066CC`).
*   [ ] Keyboard navigation works for all interactive elements.
*   [ ] No keyboard traps.
*   [ ] Color is not the only indicator of status.

## 5. Process
*   **Step 1**: Check `DESIGN_SPECIFICATIONS.md` for UI requirements.
*   **Step 2**: Check `ACCESSIBILITY_CHECKLIST.md` for compliance.
*   **Step 3**: Implement using existing patterns (React or HTMX + Alpine).
*   **Step 4**: Verify on a low-end device or throttled browser.

## 6. File Organization & Reuse
*   **Reuse First**: Before creating a new file, check if an existing template or script can be extended.
*   **Templates**:
    *   Pages: `backend/templates/` (e.g., `dashboard.html`)
    *   Fragments (HTMX): `backend/templates/fragments/` (e.g., `joint_assessment.html`)
    *   **Do not duplicate layouts**. Use `{% extends "base.html" %}`.
*   **Styles**:
    *   SCSS: `backend/static/scss/`
    *   Theme overrides: `backend/static/scss/custom-theme.scss`
    *   **Do not write inline CSS**.
*   **Scripts**:
    *   Source: `frontend/src/` (TypeScript/React)
    *   Modules: `frontend/src/modules/` (Business Logic)
    *   Components: `frontend/src/components/` (React Components)
    *   Output: `backend/static/dist/` (Bundled assets)

*   If a guideline seems unrealistic or blocks progress, **ASK the user** for permission to modify it.
*   Update this file if guidelines change.
