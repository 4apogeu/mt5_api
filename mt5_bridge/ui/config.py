"""Configuration for Order Panel UI."""

from dataclasses import dataclass


@dataclass
class PanelConfig:
    """Order panel configuration."""

    # Default trading parameters
    default_symbol: str = "BTCUSD"
    default_volume: float = 0.01
    volume_step: float = 0.01
    volume_min: float = 0.01
    volume_max: float = 10.0

    # Available symbols
    symbols: tuple = ("BTCUSD", "EURUSD", "GBPUSD", "USDJPY", "XAUUSD")

    # Server connection
    host: str = "127.0.0.1"
    port: int = 5555


@dataclass
class Colors:
    """Color scheme for the panel."""

    # Background colors
    bg_main: str = "#1e1e1e"
    bg_input: str = "#2d2d2d"
    bg_status: str = "#252525"

    # Text colors
    text_primary: str = "#ffffff"
    text_secondary: str = "#888888"
    text_success: str = "#4caf50"
    text_error: str = "#f44336"

    # Button colors
    btn_buy_bg: str = "#2e7d32"
    btn_buy_hover: str = "#388e3c"
    btn_buy_active: str = "#1b5e20"

    btn_sell_bg: str = "#c62828"
    btn_sell_hover: str = "#d32f2f"
    btn_sell_active: str = "#b71c1c"

    btn_close_bg: str = "#455a64"
    btn_close_hover: str = "#546e7a"
    btn_close_active: str = "#37474f"


# Default instances
DEFAULT_CONFIG = PanelConfig()
DEFAULT_COLORS = Colors()
