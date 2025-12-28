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

    # SL/TP defaults
    default_sl_mode: str = "percent"
    default_sl_value: float = 1.0  # 1%
    default_tp_mode: str = "percent"
    default_tp_value: float = 2.0  # 2%

    # Trailing stop defaults
    default_trailing_enabled: bool = False
    default_trailing_percent: float = 0.5  # 0.5%

    # Position panel settings
    position_refresh_interval: int = 1000  # ms
    max_positions_display: int = 20


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

    # Position panel colors
    bg_position_row: str = "#2a2a2a"
    bg_position_row_alt: str = "#252525"
    text_profit_positive: str = "#4caf50"
    text_profit_negative: str = "#f44336"
    btn_trailing_bg: str = "#3d5a80"
    btn_trailing_hover: str = "#4d6a90"

    # Mode selector colors
    mode_selected_bg: str = "#4a4a4a"
    mode_unselected_bg: str = "#2a2a2a"


# Default instances
DEFAULT_CONFIG = PanelConfig()
DEFAULT_COLORS = Colors()
