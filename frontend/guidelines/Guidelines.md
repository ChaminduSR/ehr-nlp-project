# Frontend Development Guidelines

These guidelines are derived from `DESIGN_SPECIFICATIONS.md` and `ACCESSIBILITY_CHECKLIST.md`. All frontend code must adhere to these rules.

## 1. Core Principles & Constraints
*   **Performance First**: Target <150KB total bundle size. Load time <1 second on 3G.
*   **Browser Support**: Must support **IE11** and **Windows 7**. Avoid modern JS features that require heavy polyfills unless necessary.
*   **Offline-First**: The app must function without an internet connection (Service Workers, LocalStorage).
*   **Accessibility**: WCAG AAA Compliance is mandatory.

## 2. Design & Styling
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
*   **CSS**: Use CSS variables defined in `globals.css` (or `index.css`) for colors and spacing.
*   **Components**: Keep components small and focused. Use functional React components.
*   **State Management**: Use local state or Context API. Avoid heavy state libraries (Redux) to save bundle size.
*   **HTML/JSX**: Use semantic HTML (`<main>`, `<nav>`, `<button>`, etc.).
    *   Always provide `alt` text for images.
    *   Always provide `aria-label` for icon-only buttons.
*   **Frontend Integration**:
    *   Reuse all existing files in the project.
    *   Add relevant new files or functions into the existing project structure.

## 4. Accessibility Checklist (Quick Reference)
*   [ ] All inputs have associated labels.
*   [ ] Focus indicators are visible (3px solid `#0066CC`).
*   [ ] Keyboard navigation works for all interactive elements.
*   [ ] No keyboard traps.
*   [ ] Color is not the only indicator of status.

## 5. Process
*   If a guideline seems unrealistic or blocks progress, **ASK the user** for permission to modify it.
*   Update this file if guidelines change.
