"""SL/TP calculation utilities for Order Panel."""

from enum import Enum


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class SLTPMode(str, Enum):
    """Stop-loss and take-profit input mode."""
    PERCENT = "percent"
    DOLLAR = "dollar"
    PRICE = "price"


def calculate_sl_price(
    entry_price: float,
    side: str,
    mode: str,
    value: float,
    volume: float = 0.01,
    pip_value: float = 1.0,
) -> float:
    """Calculate absolute SL price from mode and value.

    For BUY orders, the SL is placed below the entry price.
    For SELL orders, the SL is placed above the entry price.

    Args:
        entry_price: The entry price of the trade.
        side: Order side - "BUY" or "SELL".
        mode: SL calculation mode - "percent", "dollar", or "price".
        value: The value to use for calculation.
        volume: Trade volume in lots.
        pip_value: Dollar value per pip per lot.

    Returns:
        Absolute stop-loss price level.
    """
    side_upper = side.upper()
    mode_lower = mode.lower()

    if mode_lower == SLTPMode.PRICE.value:
        return value

    if mode_lower == SLTPMode.PERCENT.value:
        distance = entry_price * (value / 100.0)
    else:
        # Dollar mode
        if volume <= 0 or pip_value <= 0:
            return 0.0
        distance = value / (volume * pip_value)

    if side_upper == OrderSide.BUY.value:
        return entry_price - distance
    else:
        return entry_price + distance


def calculate_tp_price(
    entry_price: float,
    side: str,
    mode: str,
    value: float,
    volume: float = 0.01,
    pip_value: float = 1.0,
) -> float:
    """Calculate absolute TP price from mode and value.

    For BUY orders, the TP is placed above the entry price.
    For SELL orders, the TP is placed below the entry price.

    Args:
        entry_price: The entry price of the trade.
        side: Order side - "BUY" or "SELL".
        mode: TP calculation mode - "percent", "dollar", or "price".
        value: The value to use for calculation.
        volume: Trade volume in lots.
        pip_value: Dollar value per pip per lot.

    Returns:
        Absolute take-profit price level.
    """
    side_upper = side.upper()
    mode_lower = mode.lower()

    if mode_lower == SLTPMode.PRICE.value:
        return value

    if mode_lower == SLTPMode.PERCENT.value:
        distance = entry_price * (value / 100.0)
    else:
        # Dollar mode
        if volume <= 0 or pip_value <= 0:
            return 0.0
        distance = value / (volume * pip_value)

    if side_upper == OrderSide.BUY.value:
        return entry_price + distance
    else:
        return entry_price - distance


def calculate_trailing_sl(
    current_price: float,
    peak_price: float,
    side: str,
    trail_percent: float,
) -> float:
    """Calculate trailing SL based on percentage distance from peak.

    Args:
        current_price: The current market price.
        peak_price: The peak price since position opened.
        side: Order side - "BUY" or "SELL".
        trail_percent: Percentage distance from peak.

    Returns:
        Trailing stop-loss price level.
    """
    side_upper = side.upper()
    trail_distance = peak_price * (trail_percent / 100.0)

    if side_upper == OrderSide.BUY.value:
        return peak_price - trail_distance
    else:
        return peak_price + trail_distance
