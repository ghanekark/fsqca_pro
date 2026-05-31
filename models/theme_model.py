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
    border_color: str
    selection_bg: str
    selection_text: str

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
        border_color="#cccccc",
        selection_bg="#0078d4",
        selection_text="#ffffff"
    )

    DARK_PALETTE = ThemePalette(
        name="dark",
        bg_primary="#1e1e1e",
        bg_secondary="#2d2d2d",
        text_primary="#ffffff",
        text_secondary="#aaaaaa",
        accent_primary="#0078d4",
        border_color="#444444",
        selection_bg="#264f78",
        selection_text="#ffffff"
    )

    def __init__(self) -> None:
        self._palettes: Dict[str, ThemePalette] = {
            "light": self.LIGHT_PALETTE,
            "dark": self.DARK_PALETTE
        }

    def get_palette(self, name: str) -> ThemePalette:
        """Returns the palette for the given theme name. Defaults to light."""
        return self._palettes.get(name, self.LIGHT_PALETTE)
