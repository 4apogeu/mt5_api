"""Trailing Stop Manager for automatic SL updates."""

from dataclasses import dataclass
from typing import Callable, Dict, Optional


@dataclass
class TrailingState:
    """State for a position with trailing stop."""
    ticket: int
    symbol: str
    side: str  # "BUY" or "SELL"
    trail_percent: float
    peak_price: float
    current_sl: float


class TrailingStopManager:
    """Manages trailing stops for multiple positions."""

    def __init__(self, on_sl_update: Callable[[int, float], None]) -> None:
        """Initialize the trailing stop manager.

        Args:
            on_sl_update: Callback when SL should be updated (ticket, new_sl).
        """
        self._positions: Dict[int, TrailingState] = {}
        self._on_sl_update = on_sl_update

    def add_trailing(
        self,
        ticket: int,
        symbol: str,
        side: str,
        current_price: float,
        current_sl: float,
        trail_percent: float,
    ) -> None:
        """Start trailing stop for a position."""
        if side not in ("BUY", "SELL"):
            raise ValueError(f"Invalid side: {side}")

        state = TrailingState(
            ticket=ticket,
            symbol=symbol,
            side=side,
            trail_percent=trail_percent,
            peak_price=current_price,
            current_sl=current_sl,
        )
        self._positions[ticket] = state

    def remove_trailing(self, ticket: int) -> None:
        """Stop trailing for a position."""
        self._positions.pop(ticket, None)

    def update_price(self, symbol: str, price: float) -> None:
        """Update price and recalculate trailing SLs."""
        for state in self._positions.values():
            if state.symbol != symbol:
                continue

            if state.side == "BUY":
                if price > state.peak_price:
                    state.peak_price = price
                    new_sl = state.peak_price * (1 - state.trail_percent / 100)
                    if new_sl > state.current_sl:
                        state.current_sl = new_sl
                        self._on_sl_update(state.ticket, new_sl)
            else:
                if price < state.peak_price:
                    state.peak_price = price
                    new_sl = state.peak_price * (1 + state.trail_percent / 100)
                    if new_sl < state.current_sl:
                        state.current_sl = new_sl
                        self._on_sl_update(state.ticket, new_sl)

    def get_trailing_positions(self) -> list[int]:
        """Get list of tickets with trailing enabled."""
        return list(self._positions.keys())

    def is_trailing_enabled(self, ticket: int) -> bool:
        """Check if trailing is enabled for a position."""
        return ticket in self._positions

    def get_state(self, ticket: int) -> Optional[TrailingState]:
        """Get trailing state for a position."""
        return self._positions.get(ticket)
