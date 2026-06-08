# PRD 001: Dynamic Theme Engine (Dark/Light Mode)

## 1. Objective and Scope
### Objective
To implement a centralized, dynamic theme engine for `fsqca_pro` that allows users to toggle between Light and Dark modes. The system must ensure visual consistency across all windows and dialogs, persist user preferences across sessions, and follow the project's strict MVC/MVVM architecture.

### Scope
- **In-Scope:** 
    - Global stylesheet management via `QApplication`.
    - Theme selection persistence (QSettings).
    - Toggle control in the View (Main Window).
    - Base palette definitions for both Light and Dark modes.
- **Out-of-Scope:** 
    - Automatic system-theme following (to be considered for a future update).
    - Per-widget theme overrides.

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Model (`models/theme_model.py`):** 
    - Acts as a "Theme Data Store".
    - Defines color palettes (hex codes) for specific UI roles (e.g., `primary_background`, `text_main`, `border_accent`).
- **View (`views/`):** 
    - Widgets remain "theme-agnostic". 
    - Use generic QSS classes/selectors (e.g., `QPushButton { background-color: var(--primary); }`).
    - The Main Window provides the UI trigger (e.g., a menu item or toggle).
- **Controller (`controllers/theme_controller.py`):** 
    - The "Orchestrator". 
    - Reads the `ThemeModel`.
    - Performs string substitution on a template QSS file.
    - Applies the generated stylesheet to `QApplication.instance()`.
    - Handles persistence via `QSettings`.

### Implementation Detail
- **Style Injection:** Use Python's `string.Template` or f-strings to inject colors from the Model into a master QSS file.
- **Persistence:** Store the `theme_name` string in `QSettings` under the `UI` organization.
- **Signal Flow:** 
    1. User clicks "Toggle Dark Mode" in `MainWindow`.
    2. View emits `theme_toggle_requested` signal.
    3. `ThemeController` catches the signal, updates the state, saves to `QSettings`, and reapplies the global stylesheet.

---

## 3. Development Plan

### Phase 1: Infrastructure (Foundation)
1. **Create `styles/template.qss`:** Define a base stylesheet using placeholders like `${bg_color}`.
2. **Create `models/theme_model.py`:** Define a class/dataclass containing the color mappings for 'light' and 'dark'.
3. **Create `controllers/theme_controller.py`:** 
    - Implement `apply_theme(theme_name)`.
    - Implement logic to read `styles/template.qss` and perform substitution.

### Phase 2: Integration
1. **Update `main.py`:** Initialize the `ThemeController` at startup and apply the persisted theme (or default to light).
2. **Update `views/main_window.py`:** 
    - Add a "View" menu.
    - Add "Toggle Dark Mode" `QAction` (checkable).

### Phase 3: Refinement & Validation
1. **Refine QSS:** Iterate on the `template.qss` to ensure all custom QCA dialogs (Truth Table, Calibration) look polished in dark mode.
2. **Verification:**
    - Test persistence: Change theme, close app, reopen. Ensure the theme is retained.
    - Test performance: Ensure switching doesn't cause a noticeable lag or UI flicker.
    - Verify PEP 8 and Type Hinting compliance across new files.
