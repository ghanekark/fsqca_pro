# PRD 012: UI Uniformity and Semantic Styling

## 1. Objective and Scope
### Objective
To eliminate visual inconsistencies and hardcoded styling across the `fsqca_pro` application. This project will centralize all UI styling into the `ThemeController` and `template.qss`, ensuring a professional, cohesive look that responds correctly to both Light and Dark modes.

### Scope
- **In-Scope:**
    - Removing all inline `setStyleSheet()` calls from View classes.
    - Extending `ThemePalette` and `template.qss` to support semantic styles (e.g., "Primary Action", "Success", "Destructive").
    - Standardizing typography (font sizes, families) and spacing (margins, padding, border-radius).
    - Implementing semantic object naming in Qt to allow targeted styling without breaking the global theme.
- **Out-of-Scope:**
    - Adding new UI components or changing application functionality.
    - Modifying the underlying PyQt6 signal/slot logic.

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC)
- **Model (`models/theme_model.py`):**
    - Expand `ThemePalette` to include semantic colors: `success_color`, `warning_color`, `error_color`, and `link_color`.
    - Define these colors specifically for both `LIGHT_PALETTE` and `DARK_PALETTE`.
- **View (`views/`):**
    - Remove all inline `setStyleSheet` calls.
    - Use `setObjectName()` for specialized widgets (e.g., `self.apply_btn.setObjectName("PrimaryButton")`) to allow CSS-like targeting in the QSS template.
- **Controller/Style (`styles/template.qss` & `controllers/theme_controller.py`):**
    - Update the QSS template to include specific rules for custom object names (e.g., `QPushButton#PrimaryButton`).
    - Use variable substitution for all colors to maintain theme responsiveness.

### Implementation Detail
- **Semantic Mapping:**
    - `PrimaryButton`: Standard blue action button (e.g., "Analyze", "Calculate").
    - `SuccessButton`: Green confirmation button (e.g., "Apply", "Save").
    - `LinkButton`: Styling for continuum/visualizer access.
- **Typography:**
    - Define a standard `font-size` hierarchy in `template.qss` instead of hardcoding pixels in Python.

---

## 3. Development Plan

### Phase 1: Style System Expansion
1.  Update `ThemePalette` in `models/theme_model.py` with new semantic fields.
2.  Update `ThemeController.apply_theme` to pass these new variables to the template.
3.  Enhance `styles/template.qss` with specialized selectors (e.g., `QPushButton#SuccessButton`).

### Phase 2: View Sanitization
1.  Systematically audit all files in `views/` and remove `setStyleSheet` calls.
2.  Replace removed styles with `setObjectName` calls that map to the new semantic categories in `template.qss`.
3.  Fix inconsistent spacing and padding by relying on the global `QPushButton` definition.

### Phase 3: Validation & Quality Assurance
1.  Verify that both Light and Dark modes render correctly without "unreadable" hardcoded colors.
2.  Check that all buttons of the same "category" (e.g., all "Apply" buttons) look identical across different dialogs.
3.  Ensure no regressions in layout or responsiveness.

---

## 4. Success Criteria
- Zero instances of `.setStyleSheet()` in `views/*.py` (excluding global application-level setting).
- Consistent visual language across all dialogs.
- High accessibility/contrast in both themes.
