import os
from string import Template
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, QSettings, pyqtSignal
from models.theme_model import ThemeModel

class ThemeController(QObject):
    """
    Manages application themes, stylesheet generation, and persistence.
    Adheres to the Controller layer of the MVC architecture.
    """
    theme_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.model = ThemeModel()
        self.settings = QSettings("fsqca_pro", "UI")
        
        # Load template QSS
        self.template_path = os.path.join("styles", "template.qss")
        self._template_content = ""
        self._load_template()

    def _load_template(self) -> None:
        """Reads the template QSS file from disk."""
        try:
            if os.path.exists(self.template_path):
                with open(self.template_path, "r") as f:
                    self._template_content = f.read()
        except Exception as e:
            logging.error(f"Error loading theme template: {e}")

    def get_current_theme(self) -> str:
        """Returns the currently active theme name from settings."""
        return self.settings.value("theme", "light", type=str)

    def apply_theme(self, theme_name: str) -> None:
        """Generates and applies the stylesheet for the specified theme."""
        palette = self.model.get_palette(theme_name)
        
        if not self._template_content:
            self._load_template()

        # Perform variable substitution
        t = Template(self._template_content)
        qss = t.safe_substitute(
            bg_primary=palette.bg_primary,
            bg_secondary=palette.bg_secondary,
            text_primary=palette.text_primary,
            text_secondary=palette.text_secondary,
            accent_primary=palette.accent_primary,
            border_color=palette.border_color,
            selection_bg=palette.selection_bg,
            selection_text=palette.selection_text
        )

        # Apply to global application instance
        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)
            
        # Persist and notify
        self.settings.setValue("theme", theme_name)
        self.theme_changed.emit(theme_name)

    def toggle_theme(self) -> None:
        """Toggles between light and dark themes."""
        current = self.get_current_theme()
        new_theme = "dark" if current == "light" else "light"
        self.apply_theme(new_theme)
theme)
