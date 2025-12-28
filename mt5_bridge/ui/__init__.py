"""Order Panel UI for MT5 Bridge."""

from .order_panel import OrderPanel
from .config import PanelConfig, Colors, DEFAULT_CONFIG, DEFAULT_COLORS
from .widgets import (
    TradeButton, StatusBar, SymbolSelector, VolumeInput,
    ModeInput, SLTPMode, PositionRow, PositionsPanel,
)
from .utils import (
    OrderSide, SLTPMode as SLTPModeUtil,
    calculate_sl_price, calculate_tp_price, calculate_trailing_sl,
)
from .trailing_stop import TrailingStopManager, TrailingState

__all__ = [
    "OrderPanel",
    "PanelConfig",
    "Colors",
    "DEFAULT_CONFIG",
    "DEFAULT_COLORS",
    "TradeButton",
    "StatusBar",
    "SymbolSelector",
    "VolumeInput",
    "ModeInput",
    "SLTPMode",
    "PositionRow",
    "PositionsPanel",
    "OrderSide",
    "SLTPModeUtil",
    "calculate_sl_price",
    "calculate_tp_price",
    "calculate_trailing_sl",
    "TrailingStopManager",
    "TrailingState",
]
