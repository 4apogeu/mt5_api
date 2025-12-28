"""Main Order Panel UI."""

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from ..trading.bridge import MT5Bridge
from .config import PanelConfig, Colors, DEFAULT_CONFIG, DEFAULT_COLORS
from .async_bridge import AsyncBridge
from .widgets import (
    TradeButton, StatusBar, SymbolSelector, VolumeInput,
    ModeInput, SLTPMode, PositionsPanel,
)
from .utils import calculate_sl_price, calculate_tp_price
from .trailing_stop import TrailingStopManager


class OrderPanel:
    """Order panel with Buy/Sell/Close buttons."""

    def __init__(
        self,
        bridge: MT5Bridge,
        config: PanelConfig = DEFAULT_CONFIG,
        colors: Colors = DEFAULT_COLORS,
    ):
        self.bridge = bridge
        self.config = config
        self.colors = colors
        self.async_bridge = AsyncBridge()
        self.trailing_manager = TrailingStopManager(self._on_trailing_sl_update)

        self._setup_window()
        self._setup_widgets()
        self._setup_keyboard_shortcuts()

    def _setup_window(self):
        """Initialize the main window."""
        self.root = tk.Tk()
        self.root.title("MT5 Order Panel")
        self.root.configure(bg=self.colors.bg_main)
        self.root.resizable(True, True)

        # Center window
        self.root.geometry("650x480")
        self.root.eval("tk::PlaceWindow . center")

    def _setup_widgets(self):
        """Create and arrange widgets."""
        # Top row: Symbol and Volume
        top_frame = tk.Frame(self.root, bg=self.colors.bg_main)
        top_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        self.symbol_selector = SymbolSelector(
            top_frame,
            symbols=self.config.symbols,
            default=self.config.default_symbol,
            colors=self.colors,
        )
        self.symbol_selector.pack(side=tk.LEFT)

        self.volume_input = VolumeInput(
            top_frame,
            default=self.config.default_volume,
            step=self.config.volume_step,
            min_val=self.config.volume_min,
            max_val=self.config.volume_max,
            colors=self.colors,
        )
        self.volume_input.pack(side=tk.RIGHT)

        # SL/TP row
        sltp_frame = tk.Frame(self.root, bg=self.colors.bg_main)
        sltp_frame.pack(fill=tk.X, padx=15, pady=(5, 10))

        self.sl_input = ModeInput(
            sltp_frame,
            label="SL",
            default_mode=SLTPMode.PERCENTAGE,
            default_value=self.config.default_sl_value,
            step=0.1,
            colors=self.colors,
        )
        self.sl_input.pack(side=tk.LEFT, padx=(0, 10))

        self.tp_input = ModeInput(
            sltp_frame,
            label="TP",
            default_mode=SLTPMode.PERCENTAGE,
            default_value=self.config.default_tp_value,
            step=0.1,
            colors=self.colors,
        )
        self.tp_input.pack(side=tk.LEFT)

        # Trade buttons row
        btn_frame = tk.Frame(self.root, bg=self.colors.bg_main)
        btn_frame.pack(fill=tk.X, padx=15, pady=10)

        self.buy_btn = TradeButton(
            btn_frame,
            text="BUY",
            shortcut="B",
            bg_color=self.colors.btn_buy_bg,
            hover_color=self.colors.btn_buy_hover,
            active_color=self.colors.btn_buy_active,
            command=self._on_buy,
            colors=self.colors,
        )
        self.buy_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.sell_btn = TradeButton(
            btn_frame,
            text="SELL",
            shortcut="S",
            bg_color=self.colors.btn_sell_bg,
            hover_color=self.colors.btn_sell_hover,
            active_color=self.colors.btn_sell_active,
            command=self._on_sell,
            colors=self.colors,
        )
        self.sell_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.close_btn = TradeButton(
            btn_frame,
            text="CLOSE",
            shortcut="C",
            bg_color=self.colors.btn_close_bg,
            hover_color=self.colors.btn_close_hover,
            active_color=self.colors.btn_close_active,
            command=self._on_close,
            colors=self.colors,
        )
        self.close_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # Positions panel
        self.positions_panel = PositionsPanel(
            self.root,
            colors=self.colors,
            on_modify=self._on_position_modify,
            on_close=self._on_position_close,
            on_trailing_toggle=self._on_trailing_toggle,
            on_refresh=self._refresh_positions,
        )
        self.positions_panel.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Bottom row: Status bar
        self.status_bar = StatusBar(self.root, colors=self.colors)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=8)

    def _setup_keyboard_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind("<b>", lambda e: self._on_buy())
        self.root.bind("<B>", lambda e: self._on_buy())
        self.root.bind("<s>", lambda e: self._on_sell())
        self.root.bind("<S>", lambda e: self._on_sell())
        self.root.bind("<c>", lambda e: self._on_close())
        self.root.bind("<C>", lambda e: self._on_close())
        self.root.bind("<r>", lambda e: self._refresh_positions())
        self.root.bind("<R>", lambda e: self._refresh_positions())
        self.root.bind("<Escape>", lambda e: self.root.quit())

    def _get_sl_tp_prices(self, side: str, price: float, volume: float) -> tuple:
        """Calculate SL/TP prices from input modes and values."""
        sl_mode = self.sl_input.get_mode()
        sl_value = self.sl_input.get_value()
        tp_mode = self.tp_input.get_mode()
        tp_value = self.tp_input.get_value()

        # Map widget modes to util modes
        mode_map = {
            SLTPMode.PERCENTAGE: "percent",
            SLTPMode.DOLLAR: "dollar",
            SLTPMode.PRICE: "price",
        }

        sl_price = 0.0
        tp_price = 0.0

        if sl_value > 0:
            sl_price = calculate_sl_price(
                price, side, mode_map.get(sl_mode, "percent"), sl_value, volume
            )

        if tp_value > 0:
            tp_price = calculate_tp_price(
                price, side, mode_map.get(tp_mode, "percent"), tp_value, volume
            )

        return sl_price, tp_price

    def _on_buy(self):
        """Handle Buy button click."""
        symbol = self.symbol_selector.get()
        volume = self.volume_input.get()

        self.buy_btn.set_executing(True)
        self.status_bar.set_action(f"Buying {symbol}...")

        self.async_bridge.submit(
            self._execute_buy,
            symbol,
            volume,
            callback=lambda r: self._on_trade_success("BUY", r),
            error_callback=lambda e: self._on_trade_error("BUY", e),
        )

    async def _execute_buy(self, symbol: str, volume: float):
        """Execute buy with SL/TP calculation."""
        tick = await self.bridge.get_tick(symbol)
        sl, tp = self._get_sl_tp_prices("BUY", tick.ask, volume)
        return await self.bridge.buy(symbol, volume, sl, tp)

    def _on_sell(self):
        """Handle Sell button click."""
        symbol = self.symbol_selector.get()
        volume = self.volume_input.get()

        self.sell_btn.set_executing(True)
        self.status_bar.set_action(f"Selling {symbol}...")

        self.async_bridge.submit(
            self._execute_sell,
            symbol,
            volume,
            callback=lambda r: self._on_trade_success("SELL", r),
            error_callback=lambda e: self._on_trade_error("SELL", e),
        )

    async def _execute_sell(self, symbol: str, volume: float):
        """Execute sell with SL/TP calculation."""
        tick = await self.bridge.get_tick(symbol)
        sl, tp = self._get_sl_tp_prices("SELL", tick.bid, volume)
        return await self.bridge.sell(symbol, volume, sl, tp)

    def _on_close(self):
        """Handle Close button click."""
        symbol = self.symbol_selector.get()

        self.close_btn.set_executing(True)
        self.status_bar.set_action(f"Closing {symbol}...")

        self.async_bridge.submit(
            self._close_symbol_positions,
            symbol,
            callback=lambda r: self._on_close_success(r),
            error_callback=lambda e: self._on_trade_error("CLOSE", e),
        )

    async def _close_symbol_positions(self, symbol: str) -> int:
        """Close all positions for a symbol."""
        positions = await self.bridge.get_positions()
        closed = 0
        for pos in positions:
            if pos.symbol == symbol:
                await self.bridge.close_position(pos.ticket)
                closed += 1
        return closed

    def _on_trade_success(self, action: str, result):
        """Handle successful trade."""
        self.buy_btn.set_executing(False)
        self.sell_btn.set_executing(False)

        if action == "BUY":
            self.buy_btn.flash_success()
        else:
            self.sell_btn.flash_success()

        self.status_bar.set_action(
            f"{action} OK @ {result.price_executed}", success=True
        )
        # Refresh positions to show the new trade
        self._refresh_positions()

    def _on_close_success(self, closed_count: int):
        """Handle successful close."""
        self.close_btn.set_executing(False)
        self.close_btn.flash_success()

        if closed_count > 0:
            self.status_bar.set_action(f"Closed {closed_count} position(s)", success=True)
            self._refresh_positions()
        else:
            self.status_bar.set_action("No positions to close", success=True)

    def _on_trade_error(self, action: str, error: Exception):
        """Handle trade error."""
        self.buy_btn.set_executing(False)
        self.sell_btn.set_executing(False)
        self.close_btn.set_executing(False)

        if action == "BUY":
            self.buy_btn.flash_error()
        elif action == "SELL":
            self.sell_btn.flash_error()
        else:
            self.close_btn.flash_error()

        self.status_bar.set_action(f"{action} FAILED", success=False)
        messagebox.showerror("Trade Error", str(error))

    def _on_connected(self, _):
        """Handle connection success."""
        self.status_bar.set_connected(True)
        self.status_bar.set_action("Ready")
        # Start positions refresh
        self._schedule_positions_refresh()

    def _on_connection_error(self, error: Exception):
        """Handle connection error."""
        self.status_bar.set_connected(False)
        self.status_bar.set_action(f"Connection failed: {error}", success=False)

    # --- Position Panel Callbacks ---

    def _refresh_positions(self):
        """Refresh the positions list."""
        self.async_bridge.submit(
            self._fetch_positions,
            callback=self._update_positions_panel,
            error_callback=lambda e: self.status_bar.set_action(f"Refresh failed: {e}", success=False),
        )

    async def _fetch_positions(self):
        """Fetch all open positions."""
        positions = await self.bridge.get_positions()
        return [
            {
                "ticket": p.ticket,
                "symbol": p.symbol,
                "order_type": p.order_type,
                "volume": p.volume,
                "open_price": p.open_price,
                "stop_loss": p.stop_loss,
                "take_profit": p.take_profit,
                "profit": p.profit,
            }
            for p in positions
        ]

    def _update_positions_panel(self, positions: list):
        """Update positions panel with fetched data."""
        self.positions_panel.update_positions(positions)

    def _on_position_modify(self, ticket: int, sl: float, tp: float):
        """Handle position SL/TP modification."""
        self.status_bar.set_action(f"Modifying position #{ticket}...")
        self.async_bridge.submit(
            self.bridge.modify_position,
            ticket,
            sl,
            tp,
            callback=lambda _: self._on_modify_success(ticket),
            error_callback=lambda e: self._on_modify_error(ticket, e),
        )

    def _on_modify_success(self, ticket: int):
        """Handle successful position modification."""
        self.status_bar.set_action(f"Position #{ticket} modified", success=True)
        self._refresh_positions()

    def _on_modify_error(self, ticket: int, error: Exception):
        """Handle position modification error."""
        self.status_bar.set_action(f"Modify #{ticket} failed", success=False)
        messagebox.showerror("Modify Error", str(error))

    def _on_position_close(self, ticket: int):
        """Handle single position close."""
        self.status_bar.set_action(f"Closing position #{ticket}...")
        self.async_bridge.submit(
            self.bridge.close_position,
            ticket,
            callback=lambda _: self._on_single_close_success(ticket),
            error_callback=lambda e: self._on_modify_error(ticket, e),
        )

    def _on_single_close_success(self, ticket: int):
        """Handle successful single position close."""
        self.status_bar.set_action(f"Position #{ticket} closed", success=True)
        self.trailing_manager.remove_trailing(ticket)
        self._refresh_positions()

    def _on_trailing_toggle(self, ticket: int, enabled: bool, percent: float):
        """Handle trailing stop toggle."""
        if enabled:
            # Get current position info to initialize trailing
            self.async_bridge.submit(
                self._enable_trailing,
                ticket,
                percent,
                callback=lambda _: self.status_bar.set_action(f"Trailing enabled #{ticket} @ {percent}%"),
                error_callback=lambda e: self.status_bar.set_action(f"Trailing failed: {e}", success=False),
            )
        else:
            self.trailing_manager.remove_trailing(ticket)
            self.status_bar.set_action(f"Trailing disabled #{ticket}")

    async def _enable_trailing(self, ticket: int, percent: float):
        """Enable trailing stop for a position."""
        positions = await self.bridge.get_positions()
        for p in positions:
            if p.ticket == ticket:
                tick = await self.bridge.get_tick(p.symbol)
                price = tick.bid if p.order_type.upper() == "BUY" else tick.ask
                self.trailing_manager.add_trailing(
                    ticket, p.symbol, p.order_type.upper(),
                    price, p.stop_loss or 0, percent
                )
                return
        raise ValueError(f"Position #{ticket} not found")

    def _on_trailing_sl_update(self, ticket: int, new_sl: float):
        """Handle trailing stop SL update from manager."""
        self.async_bridge.submit(
            self.bridge.modify_position,
            ticket,
            new_sl,
            None,  # Don't change TP
            callback=lambda _: self.status_bar.set_action(f"Trailing SL updated #{ticket}"),
            error_callback=lambda e: self.status_bar.set_action(f"Trailing update failed", success=False),
        )

    def _schedule_positions_refresh(self):
        """Schedule periodic positions refresh."""
        self._refresh_positions()
        self.root.after(self.config.position_refresh_interval, self._schedule_positions_refresh)

    def run(self):
        """Start the panel and connect to MT5."""
        # Start async bridge
        self.async_bridge.start()

        # Start result processing
        self.root.after(50, lambda: self.async_bridge.process_results(self.root))

        # Connect to MT5
        self.status_bar.set_action("Connecting...")
        self.async_bridge.submit(
            self._connect,
            callback=self._on_connected,
            error_callback=self._on_connection_error,
        )

        # Run mainloop
        try:
            self.root.mainloop()
        finally:
            self.async_bridge.stop()

    async def _connect(self):
        """Connect to MT5 server and wait for EA."""
        await self.bridge.start()
        await self.bridge.wait_for_connection(timeout=60)
        return True
