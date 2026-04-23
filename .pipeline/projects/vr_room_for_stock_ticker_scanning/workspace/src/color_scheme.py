"""Color scheme for ticker display — maps price changes to colors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Color:
    """RGB color representation."""
    r: int
    g: int
    b: int

    def to_tuple(self) -> Tuple[int, int, int]:
        """Convert to RGB tuple."""
        return (self.r, self.g, self.b)

    def to_hex(self) -> str:
        """Convert to hex string."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


class TickerColorScheme:
    """Color scheme for ticker price changes."""

    # Base colors
    GREEN = Color(0, 255, 0)
    RED = Color(255, 0, 0)
    WHITE = Color(255, 255, 255)
    BLACK = Color(0, 0, 0)
    GRAY = Color(128, 128, 128)
    DARK_GRAY = Color(64, 64, 64)
    LIGHT_GRAY = Color(192, 192, 192)

    # Background colors
    BG_UP = Color(0, 50, 0)
    BG_DOWN = Color(50, 0, 0)
    BG_NEUTRAL = Color(30, 30, 30)

    @classmethod
    def get_price_color(cls, change_percent: float) -> Color:
        """Get color for price change percentage.

        Args:
            change_percent: Price change as percentage

        Returns:
            Color for the price change
        """
        if change_percent > 0:
            # Green with intensity based on magnitude
            intensity = min(abs(change_percent) / 10.0, 1.0)
            return Color(
                r=int(255 * (1 - intensity)),
                g=255,
                b=int(255 * (1 - intensity)),
            )
        elif change_percent < 0:
            # Red with intensity based on magnitude
            intensity = min(abs(change_percent) / 10.0, 1.0)
            return Color(
                r=255,
                g=int(255 * (1 - intensity)),
                b=int(255 * (1 - intensity)),
            )
        else:
            return cls.WHITE

    @classmethod
    def get_background_color(cls, change_percent: float) -> Color:
        """Get background color for ticker panel based on price change.

        Args:
            change_percent: Price change as percentage

        Returns:
            Background color for the panel
        """
        if change_percent > 0:
            intensity = min(abs(change_percent) / 10.0, 1.0)
            return Color(
                r=int(50 * intensity),
                g=int(100 + 155 * intensity),
                b=int(50 * intensity),
            )
        elif change_percent < 0:
            intensity = min(abs(change_percent) / 10.0, 1.0)
            return Color(
                r=int(100 + 155 * intensity),
                g=int(50 * (1 - intensity)),
                b=int(50 * (1 - intensity)),
            )
        else:
            return cls.BG_NEUTRAL

    @classmethod
    def get_text_color(cls, change_percent: float) -> Color:
        """Get text color for ticker panel based on price change.

        Args:
            change_percent: Price change as percentage

        Returns:
            Text color for the panel
        """
        if abs(change_percent) > 5:
            return cls.WHITE
        return cls.LIGHT_GRAY
