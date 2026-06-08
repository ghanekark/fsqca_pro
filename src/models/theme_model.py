from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class ThemePalette:
    name: str
    bg_primary: str
    bg_secondary: str
    text_primary: str
    text_secondary: str
    accent_primary: str
    accent_hover: str
    border_color: str
    selection_bg: str
    selection_text: str
    success_color: str
    warning_color: str
    error_color: str
    link_color: str

class ThemeModel:
    """
    Stores color palettes for different application themes.
    Adheres to the Model layer of the MVC architecture.
    """
    
    LIGHT_PALETTE = ThemePalette(
        name="light",
        bg_primary="#ffffff",
        bg_secondary="#f0f0f0",
        text_primary="#000000",
        text_secondary="#555555",
        accent_primary="#0078d4",
        accent_hover="#106ebe",
        border_color="#cccccc",
        selection_bg="#0078d4",
        selection_text="#ffffff",
        success_color="#107c10",
        warning_color="#ff8c00",
        error_color="#d13438",
        link_color="#005a9e"
    )

    DARK_PALETTE = ThemePalette(
        name="dark",
        bg_primary="#1e1e1e",
        bg_secondary="#2d2d2d",
        text_primary="#ffffff",
        text_secondary="#aaaaaa",
        accent_primary="#0078d4",
        accent_hover="#47aef7",
        border_color="#444444",
        selection_bg="#264f78",
        selection_text="#ffffff",
        success_color="#3ff23f",
        warning_color="#ffaa44",
        error_color="#ff5f5f",
        link_color="#47aef7"
    )

    def __init__(self) -> None:
        self._palettes: Dict[str, ThemePalette] = {
            "light": self.LIGHT_PALETTE,
            "dark": self.DARK_PALETTE
        }

    def get_palette(self, name: str) -> ThemePalette:
        """Returns the palette for the given theme name. Defaults to light."""
        return self._palettes.get(name, self.LIGHT_PALETTE)
