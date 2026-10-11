# UX and Design Specification — The Lenny Growth Assistant

## 1. Visual Design Philosophy
The Lenny Growth Assistant interface follows a modern, dark-mode SaaS design system optimized for readability, information density, and focus.

### Color Tokens
- **Background Deep:** `#0b1120` (Sidebar & Artifact Viewer backdrop)
- **Background Primary:** `#0f172a` (Chat area main canvas)
- **Background Secondary:** `#1e293b` (Message bubbles, inputs, and cards)
- **Brand Accent:** `#6366f1` (Indigo primary) with linear gradient to `#a855f7` (Purple)
- **Text Primary:** `#f8fafc` (High-contrast slate white)
- **Text Muted:** `#64748b` (Metadata, timestamps, secondary labels)

---

## 2. Layout & Components

### 2.1. Sidebar (Width: 280px)
- **Brand Header:** Icon avatar with glowing gradient border.
- **New Chat Action:** Prominent gradient button triggering instant session generation.
- **Session List:** Scrollable list of user conversations with hover delete actions.
- **Provider Selector:** Bottom footer dropdown displaying active provider and model status.

### 2.2. Chat Area
- **Header:** Session title with live system status badge (`System Ready` / `DB Connected`).
- **Empty State:** Clean introduction card with prompt suggestion pills.
- **Message Bubbles:**
  - User message: Right-aligned indigo gradient bubble.
  - Assistant message: Left-aligned card with avatar and timestamp.
  - Citations Accordion: Expandable shelf displaying episode title, chunk locator, and direct quote excerpts.

### 2.3. Artifact Viewer (Width: 520px Desktop)
- Located side-by-side with chat on desktop screens (>900px).
- Sandboxed iframe view for HTML widgets, interactive tables, and visual mockups.
- Formatted markdown reader for long-form essays and playbooks.
- Action toolbar: One-click "Copy" and "Download" buttons.
- Mobile adaptation: Toggles into a full-width overlay drawer with a close button.

---

## 3. Accessibility & Usability (a11y)
- **Keyboard Navigation:** Full tab support across session items, buttons, and input areas.
- **Contrast Ratios:** Exceeds WCAG AA 4.5:1 standards on dark backgrounds.
- **Focus Indicators:** 2px glowing indigo outline on active inputs.
- **Error States:** High-visibility dismissible toast banner for network or provider failures.
