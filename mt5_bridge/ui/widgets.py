"""Custom widgets for Order Panel."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from .config import Colors, DEFAULT_COLORS


class TradeButton(tk.Button):
    """Trade button with visual feedback and keyboard shortcut."""

    def __init__(
        self,
        parent,
        text: str,
        shortcut: str,
        bg_color: str,
        hover_color: str,
        active_color: str,
        command: Optional[Callable] = None,
        colors: Colors = DEFAULT_COLORS,
        **kwargs,
    ):
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.colors = colors
        self._executing = False

        super().__init__(
            parent,
            text=f"{shortcut} {text}",
            command=command,
            bg=bg_color,
            fg=colors.text_primary,
            activebackground=active_color,
            activeforeground=colors.text_primary,
            relief=tk.FLAT,
            font=("Helvetica", 12, "bold"),
            cursor="hand2",
            padx=20,
            pady=10,
            **kwargs,
        )

        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        if not self._executing:
            self.config(bg=self.hover_color)

    def _on_leave(self, event):
        if not self._executing:
            self.config(bg=self.bg_color)

    def set_executing(self, executing: bool):
        """Set button to executing state (pulsing effect)."""
        self._executing = executing
        if executing:
            self.config(bg=self.active_color, state=tk.DISABLED)
        else:
            self.config(bg=self.bg_color, state=tk.NORMAL)

    def flash_success(self):
        """Flash green to indicate success."""
        self.config(bg=self.colors.text_success)
        self.after(300, lambda: self.config(bg=self.bg_color))

    def flash_error(self):
        """Flash red to indicate error."""
        self.config(bg=self.colors.text_error)
        self.after(300, lambda: self.config(bg=self.bg_color))


class StatusBar(tk.Frame):
    """Status bar showing connection and last action status."""

    def __init__(self, parent, colors: Colors = DEFAULT_COLORS, **kwargs):
        super().__init__(parent, bg=colors.bg_status, **kwargs)
        self.colors = colors

        # Connection status
        self.conn_label = tk.Label(
            self,
            text="Disconnected",
            bg=colors.bg_status,
            fg=colors.text_error,
            font=("Helvetica", 10),
        )
        self.conn_label.pack(side=tk.LEFT, padx=10)

        # Separator
        tk.Label(
            self,
            text="|",
            bg=colors.bg_status,
            fg=colors.text_secondary,
            font=("Helvetica", 10),
        ).pack(side=tk.LEFT)

        # Last action status
        self.action_label = tk.Label(
            self,
            text="Ready",
            bg=colors.bg_status,
            fg=colors.text_secondary,
            font=("Helvetica", 10),
        )
        self.action_label.pack(side=tk.LEFT, padx=10)

    def set_connected(self, connected: bool):
        """Update connection status."""
        if connected:
            self.conn_label.config(text="Connected", fg=self.colors.text_success)
        else:
            self.conn_label.config(text="Disconnected", fg=self.colors.text_error)

    def set_action(self, text: str, success: bool = True):
        """Update last action status."""
        color = self.colors.text_success if success else self.colors.text_error
        self.action_label.config(text=text, fg=color)


class SymbolSelector(tk.Frame):
    """Symbol selector with searchable autocomplete dropdown."""

    def __init__(
        self,
        parent,
        symbols: tuple = (),
        default: str = "",
        on_change: Optional[Callable[[str], None]] = None,
        colors: Colors = DEFAULT_COLORS,
        **kwargs,
    ):
        super().__init__(parent, bg=colors.bg_main, **kwargs)
        self.colors = colors
        self.on_change = on_change
        self._all_symbols: list[str] = list(symbols)
        self._filtered_symbols: list[str] = list(symbols)

        tk.Label(
            self,
            text="Symbol:",
            bg=colors.bg_main,
            fg=colors.text_primary,
            font=("Helvetica", 11),
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.var = tk.StringVar(value=default)
        self.combo = ttk.Combobox(
            self,
            textvariable=self.var,
            values=symbols,
            width=12,
            font=("Helvetica", 11),
        )
        self.combo.pack(side=tk.LEFT)
        self.combo.bind("<<ComboboxSelected>>", self._on_select)
        self.combo.bind("<KeyRelease>", self._on_keyrelease)
        self.combo.bind("<Return>", self._on_enter)

    def _on_select(self, event):
        if self.on_change:
            self.on_change(self.var.get())

    def _on_keyrelease(self, event):
        """Filter dropdown as user types."""
        if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Escape"):
            return

        typed = self.var.get().upper()
        if not typed:
            self._filtered_symbols = self._all_symbols.copy()
        else:
            self._filtered_symbols = [s for s in self._all_symbols if typed in s.upper()]

        self.combo["values"] = self._filtered_symbols

        # Show dropdown if there are matches
        if self._filtered_symbols and typed:
            self.combo.event_generate("<Down>")

    def _on_enter(self, event):
        """Handle Enter key - select first match or keep typed value."""
        typed = self.var.get().upper()
        # If exact match exists, use it
        for s in self._all_symbols:
            if s.upper() == typed:
                self.var.set(s)
                if self.on_change:
                    self.on_change(s)
                return
        # Otherwise use first filtered match
        if self._filtered_symbols:
            self.var.set(self._filtered_symbols[0])
            if self.on_change:
                self.on_change(self._filtered_symbols[0])

    def get(self) -> str:
        return self.var.get()

    def set_symbols(self, symbols: list[str]) -> None:
        """Update the available symbols list."""
        self._all_symbols = symbols.copy()
        self._filtered_symbols = symbols.copy()
        self.combo["values"] = symbols
        # If current value not in new list, set to first symbol
        if self.var.get() not in symbols and symbols:
            self.var.set(symbols[0])
            if self.on_change:
                self.on_change(symbols[0])


class VolumeInput(tk.Frame):
    """Volume input with increment/decrement buttons."""

    def __init__(
        self,
        parent,
        default: float,
        step: float,
        min_val: float,
        max_val: float,
        on_volume_change: Optional[Callable[[float], None]] = None,
        colors: Colors = DEFAULT_COLORS,
        **kwargs,
    ):
        super().__init__(parent, bg=colors.bg_main, **kwargs)
        self.colors = colors
        self.step = step
        self.min_val = min_val
        self.max_val = max_val
        self.on_volume_change = on_volume_change

        tk.Label(
            self,
            text="Volume:",
            bg=colors.bg_main,
            fg=colors.text_primary,
            font=("Helvetica", 11),
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Decrement button
        tk.Button(
            self,
            text="-",
            command=self._decrement,
            bg=colors.bg_input,
            fg=colors.text_primary,
            relief=tk.FLAT,
            font=("Helvetica", 10, "bold"),
            width=2,
        ).pack(side=tk.LEFT)

        # Volume entry
        self.var = tk.StringVar(value=f"{default:.2f}")
        self.entry = tk.Entry(
            self,
            textvariable=self.var,
            width=8,
            justify=tk.CENTER,
            bg=colors.bg_input,
            fg=colors.text_primary,
            insertbackground=colors.text_primary,
            relief=tk.FLAT,
            font=("Helvetica", 11),
        )
        self.entry.pack(side=tk.LEFT, padx=2)
        # Bind entry changes (on focus out or Enter key)
        self.entry.bind("<FocusOut>", self._on_entry_change)
        self.entry.bind("<Return>", self._on_entry_change)

        # Increment button
        tk.Button(
            self,
            text="+",
            command=self._increment,
            bg=colors.bg_input,
            fg=colors.text_primary,
            relief=tk.FLAT,
            font=("Helvetica", 10, "bold"),
            width=2,
        ).pack(side=tk.LEFT)

    def _decrement(self):
        try:
            val = float(self.var.get()) - self.step
            val = max(self.min_val, val)
            self.var.set(f"{val:.2f}")
        except ValueError:
            val = self.min_val
            self.var.set(f"{val:.2f}")
        self._notify_change(val)

    def _increment(self):
        try:
            val = float(self.var.get()) + self.step
            val = min(self.max_val, val)
            self.var.set(f"{val:.2f}")
        except ValueError:
            val = self.min_val
            self.var.set(f"{val:.2f}")
        self._notify_change(val)

    def _notify_change(self, volume: float):
        """Notify callback of volume change."""
        if self.on_volume_change:
            self.on_volume_change(volume)

    def _on_entry_change(self, event=None):
        """Handle entry value change."""
        try:
            val = float(self.var.get())
            val = max(self.min_val, min(self.max_val, val))
            self._notify_change(val)
        except ValueError:
            pass  # Ignore invalid input

    def get(self) -> float:
        try:
            return float(self.var.get())
        except ValueError:
            return self.min_val


class SLTPMode:
    """Mode for Stop Loss and Take Profit values."""
    PERCENTAGE = "%"
    DOLLAR = "$"
    PRICE = "Price"


class ModeInput(tk.Frame):
    """Input widget with mode selector for SL/TP values."""

    def __init__(
        self,
        parent,
        label: str,
        default_mode: str = "%",
        default_value: float = 0.0,
        step: float = 0.1,
        min_val: float = 0.0,
        max_val: float = 10000.0,
        on_change: Optional[Callable[[], None]] = None,
        colors: Colors = DEFAULT_COLORS,
        **kwargs,
    ):
        super().__init__(parent, bg=colors.bg_main, **kwargs)
        self.colors = colors
        self.step = step
        self.min_val = min_val
        self.max_val = max_val
        self.on_change = on_change

        # Label
        tk.Label(
            self,
            text=f"{label}:",
            bg=colors.bg_main,
            fg=colors.text_primary,
            font=("Helvetica", 10),
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Mode selector
        self._mode_var = tk.StringVar(value=default_mode)
        mode_frame = tk.Frame(self, bg=colors.bg_main)
        mode_frame.pack(side=tk.LEFT, padx=(0, 5))

        for mode in [SLTPMode.PERCENTAGE, SLTPMode.DOLLAR, SLTPMode.PRICE]:
            rb = tk.Radiobutton(
                mode_frame,
                text=mode,
                variable=self._mode_var,
                value=mode,
                command=self._on_mode_change,
                bg=colors.bg_main,
                fg=colors.text_primary,
                selectcolor=colors.bg_input,
                activebackground=colors.bg_main,
                activeforeground=colors.text_primary,
                font=("Helvetica", 9),
                indicatoron=0,
                padx=6,
                pady=2,
            )
            rb.pack(side=tk.LEFT, padx=1)

        # Decrement button
        tk.Button(
            self,
            text="-",
            command=self._decrement,
            bg=colors.bg_input,
            fg=colors.text_primary,
            relief=tk.FLAT,
            font=("Helvetica", 10, "bold"),
            width=2,
        ).pack(side=tk.LEFT)

        # Value entry
        self._value_var = tk.StringVar(value=f"{default_value:.2f}")
        self.entry = tk.Entry(
            self,
            textvariable=self._value_var,
            width=8,
            justify=tk.CENTER,
            bg=colors.bg_input,
            fg=colors.text_primary,
            insertbackground=colors.text_primary,
            relief=tk.FLAT,
            font=("Helvetica", 10),
        )
        self.entry.pack(side=tk.LEFT, padx=2)

        # Increment button
        tk.Button(
            self,
            text="+",
            command=self._increment,
            bg=colors.bg_input,
            fg=colors.text_primary,
            relief=tk.FLAT,
            font=("Helvetica", 10, "bold"),
            width=2,
        ).pack(side=tk.LEFT)

    def _on_mode_change(self):
        if self.on_change:
            self.on_change()

    def _decrement(self):
        try:
            val = float(self._value_var.get()) - self.step
            val = max(self.min_val, val)
            self._value_var.set(f"{val:.2f}")
        except ValueError:
            self._value_var.set(f"{self.min_val:.2f}")

    def _increment(self):
        try:
            val = float(self._value_var.get()) + self.step
            val = min(self.max_val, val)
            self._value_var.set(f"{val:.2f}")
        except ValueError:
            self._value_var.set(f"{self.min_val:.2f}")

    def get_mode(self) -> str:
        return self._mode_var.get()

    def get_value(self) -> float:
        try:
            return float(self._value_var.get())
        except ValueError:
            return self.min_val

    def set_value(self, value: float) -> None:
        clamped = max(self.min_val, min(self.max_val, value))
        self._value_var.set(f"{clamped:.2f}")

    def set_mode(self, mode: str) -> None:
        self._mode_var.set(mode)


class PositionModifyDialog(tk.Toplevel):
    """Modal dialog for modifying position SL/TP and trailing stop."""

    def __init__(
        self,
        parent,
        position: dict,
        colors: Optional[Colors] = None,
        on_apply: Optional[Callable[[int, float, float, bool, float], None]] = None,
        **kwargs,
    ):
        """Initialize the position modify dialog.

        Args:
            parent: Parent widget
            position: Position data dict with keys: ticket, symbol, order_type,
                      volume, open_price, profit, stop_loss, take_profit
            colors: Color scheme
            on_apply: Callback(ticket, sl, tp, trailing_enabled, trailing_percent)
        """
        self.colors = colors if colors is not None else DEFAULT_COLORS
        super().__init__(parent, bg=self.colors.bg_main, **kwargs)

        self.position = position
        self.ticket = position.get("ticket", 0)
        self.on_apply = on_apply
        self.result = None  # Will store (sl, tp, trailing_enabled, trailing_percent) on Apply

        self._build_ui()
        self._center_on_parent(parent)
        self._make_modal()

    def _build_ui(self) -> None:
        """Build the dialog UI."""
        self.title(f"Modify Position #{self.ticket}")
        self.resizable(False, False)

        bg = self.colors.bg_main
        font = ("Helvetica", 10)
        font_bold = ("Helvetica", 10, "bold")

        # Main container with padding
        container = tk.Frame(self, bg=bg, padx=20, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Position info section
        info_frame = tk.Frame(container, bg=bg)
        info_frame.pack(fill=tk.X, pady=(0, 15))

        # Symbol and type row
        symbol_type_frame = tk.Frame(info_frame, bg=bg)
        symbol_type_frame.pack(fill=tk.X)

        symbol = self.position.get("symbol", "")
        order_type = self.position.get("order_type", "")
        type_color = self.colors.text_success if order_type.upper() == "BUY" else self.colors.text_error

        tk.Label(
            symbol_type_frame, text=symbol, bg=bg, fg=self.colors.text_primary,
            font=("Helvetica", 14, "bold")
        ).pack(side=tk.LEFT)

        tk.Label(
            symbol_type_frame, text=f"  {order_type}", bg=bg, fg=type_color,
            font=("Helvetica", 14, "bold")
        ).pack(side=tk.LEFT)

        # Volume and entry price row
        vol_entry_frame = tk.Frame(info_frame, bg=bg)
        vol_entry_frame.pack(fill=tk.X, pady=(5, 0))

        volume = self.position.get("volume", 0)
        open_price = self.position.get("open_price", 0)

        tk.Label(
            vol_entry_frame, text=f"Volume: {volume:.2f}", bg=bg,
            fg=self.colors.text_secondary, font=font
        ).pack(side=tk.LEFT)

        tk.Label(
            vol_entry_frame, text=f"   Entry: {open_price:.5f}", bg=bg,
            fg=self.colors.text_secondary, font=font
        ).pack(side=tk.LEFT)

        # Current profit row
        profit = self.position.get("profit", 0.0)
        profit_color = self.colors.text_profit_positive if profit >= 0 else self.colors.text_profit_negative

        profit_frame = tk.Frame(info_frame, bg=bg)
        profit_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Label(
            profit_frame, text="Current P/L: ", bg=bg,
            fg=self.colors.text_secondary, font=font
        ).pack(side=tk.LEFT)

        tk.Label(
            profit_frame, text=f"${profit:+.2f}", bg=bg,
            fg=profit_color, font=font_bold
        ).pack(side=tk.LEFT)

        # Separator
        tk.Frame(container, bg=self.colors.text_secondary, height=1).pack(fill=tk.X, pady=10)

        # SL/TP input section
        sltp_frame = tk.Frame(container, bg=bg)
        sltp_frame.pack(fill=tk.X, pady=(0, 10))

        # Stop Loss row
        sl_row = tk.Frame(sltp_frame, bg=bg)
        sl_row.pack(fill=tk.X, pady=5)

        tk.Label(
            sl_row, text="Stop Loss:", bg=bg, fg=self.colors.text_primary,
            font=font, width=12, anchor=tk.W
        ).pack(side=tk.LEFT)

        current_sl = self.position.get("stop_loss", 0) or 0
        self.sl_var = tk.StringVar(value=str(current_sl) if current_sl else "")
        self.sl_entry = tk.Entry(
            sl_row, textvariable=self.sl_var, width=15, justify=tk.CENTER,
            bg=self.colors.bg_input, fg=self.colors.text_primary,
            insertbackground=self.colors.text_primary, relief=tk.FLAT, font=font
        )
        self.sl_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(
            sl_row, text="(price or 0 to clear)", bg=bg,
            fg=self.colors.text_secondary, font=("Helvetica", 9)
        ).pack(side=tk.LEFT, padx=5)

        # Take Profit row
        tp_row = tk.Frame(sltp_frame, bg=bg)
        tp_row.pack(fill=tk.X, pady=5)

        tk.Label(
            tp_row, text="Take Profit:", bg=bg, fg=self.colors.text_primary,
            font=font, width=12, anchor=tk.W
        ).pack(side=tk.LEFT)

        current_tp = self.position.get("take_profit", 0) or 0
        self.tp_var = tk.StringVar(value=str(current_tp) if current_tp else "")
        self.tp_entry = tk.Entry(
            tp_row, textvariable=self.tp_var, width=15, justify=tk.CENTER,
            bg=self.colors.bg_input, fg=self.colors.text_primary,
            insertbackground=self.colors.text_primary, relief=tk.FLAT, font=font
        )
        self.tp_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(
            tp_row, text="(price or 0 to clear)", bg=bg,
            fg=self.colors.text_secondary, font=("Helvetica", 9)
        ).pack(side=tk.LEFT, padx=5)

        # Separator
        tk.Frame(container, bg=self.colors.text_secondary, height=1).pack(fill=tk.X, pady=10)

        # Trailing stop section
        trailing_frame = tk.Frame(container, bg=bg)
        trailing_frame.pack(fill=tk.X, pady=(0, 15))

        self.trailing_var = tk.BooleanVar(value=False)
        trailing_check = tk.Checkbutton(
            trailing_frame, text="Enable Trailing Stop", variable=self.trailing_var,
            bg=bg, fg=self.colors.text_primary, selectcolor=self.colors.bg_input,
            activebackground=bg, activeforeground=self.colors.text_primary, font=font
        )
        trailing_check.pack(side=tk.LEFT)

        tk.Label(
            trailing_frame, text="  Distance:", bg=bg,
            fg=self.colors.text_primary, font=font
        ).pack(side=tk.LEFT)

        self.trailing_percent_var = tk.StringVar(value="1.0")
        self.trailing_entry = tk.Entry(
            trailing_frame, textvariable=self.trailing_percent_var, width=6, justify=tk.CENTER,
            bg=self.colors.bg_input, fg=self.colors.text_primary,
            insertbackground=self.colors.text_primary, relief=tk.FLAT, font=font
        )
        self.trailing_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(
            trailing_frame, text="%", bg=bg,
            fg=self.colors.text_secondary, font=font
        ).pack(side=tk.LEFT)

        # Button section
        btn_frame = tk.Frame(container, bg=bg)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        # Cancel button
        cancel_btn = tk.Button(
            btn_frame, text="Cancel", command=self._on_cancel,
            bg=self.colors.btn_close_bg, fg=self.colors.text_primary,
            activebackground=self.colors.btn_close_hover,
            activeforeground=self.colors.text_primary,
            relief=tk.FLAT, font=font_bold, padx=20, pady=8, cursor="hand2"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Apply button
        apply_btn = tk.Button(
            btn_frame, text="Apply", command=self._on_apply,
            bg=self.colors.btn_buy_bg, fg=self.colors.text_primary,
            activebackground=self.colors.btn_buy_hover,
            activeforeground=self.colors.text_primary,
            relief=tk.FLAT, font=font_bold, padx=20, pady=8, cursor="hand2"
        )
        apply_btn.pack(side=tk.RIGHT)

        # Bind keyboard shortcuts
        self.bind("<Return>", lambda e: self._on_apply())
        self.bind("<Escape>", lambda e: self._on_cancel())

        # Focus SL entry
        self.sl_entry.focus_set()

    def _center_on_parent(self, parent) -> None:
        """Center dialog on parent window."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()

        # Get parent position
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Calculate center position
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        self.geometry(f"+{x}+{y}")

    def _make_modal(self) -> None:
        """Make dialog modal."""
        self.transient(self.master)
        self.grab_set()

    def _on_apply(self) -> None:
        """Handle Apply button click."""
        try:
            sl = float(self.sl_var.get()) if self.sl_var.get() else 0.0
        except ValueError:
            sl = 0.0

        try:
            tp = float(self.tp_var.get()) if self.tp_var.get() else 0.0
        except ValueError:
            tp = 0.0

        try:
            trailing_percent = float(self.trailing_percent_var.get()) if self.trailing_percent_var.get() else 1.0
        except ValueError:
            trailing_percent = 1.0

        trailing_enabled = self.trailing_var.get()

        self.result = (sl, tp, trailing_enabled, trailing_percent)

        if self.on_apply:
            self.on_apply(self.ticket, sl, tp, trailing_enabled, trailing_percent)

        self.destroy()

    def _on_cancel(self) -> None:
        """Handle Cancel button click."""
        self.result = None
        self.destroy()


class PositionRow(tk.Frame):
    """Single position row with Edit button for SL/TP modification."""

    def __init__(
        self,
        parent,
        position: dict,
        colors: Optional[Colors] = None,
        on_modify: Optional[Callable[[int, float, float], None]] = None,
        on_close: Optional[Callable[[int], None]] = None,
        on_trailing_toggle: Optional[Callable[[int, bool, float], None]] = None,
        **kwargs,
    ):
        self.colors = colors if colors is not None else DEFAULT_COLORS
        super().__init__(parent, bg=self.colors.bg_position_row, **kwargs)

        self.position = position
        self.ticket = position.get("ticket", 0)
        self.on_modify = on_modify
        self.on_close = on_close
        self.on_trailing_toggle = on_trailing_toggle

        self._build_ui()

    def _build_ui(self) -> None:
        position = self.position
        bg = self.colors.bg_position_row
        font = ("Helvetica", 9)

        # Symbol
        tk.Label(self, text=position.get("symbol", ""), bg=bg,
                 fg=self.colors.text_primary, font=font, width=8).pack(side=tk.LEFT, padx=2)

        # Type (colored)
        order_type = position.get("order_type", "")
        type_color = self.colors.text_success if order_type.upper() == "BUY" else self.colors.text_error
        tk.Label(self, text=order_type, bg=bg, fg=type_color,
                 font=("Helvetica", 9, "bold"), width=5).pack(side=tk.LEFT, padx=2)

        # Volume
        tk.Label(self, text=f"{position.get('volume', 0):.2f}", bg=bg,
                 fg=self.colors.text_primary, font=font, width=5).pack(side=tk.LEFT, padx=2)

        # Entry
        tk.Label(self, text=f"{position.get('open_price', 0):.2f}", bg=bg,
                 fg=self.colors.text_primary, font=font, width=8).pack(side=tk.LEFT, padx=2)

        # P/L
        profit = position.get("profit", 0.0)
        pl_color = self.colors.text_profit_positive if profit >= 0 else self.colors.text_profit_negative
        self.profit_label = tk.Label(self, text=f"${profit:+.2f}", bg=bg, fg=pl_color, font=font, width=8)
        self.profit_label.pack(side=tk.LEFT, padx=2)

        # SL Label (display only)
        sl_value = position.get("stop_loss", 0) or 0
        sl_text = f"{sl_value:.5f}" if sl_value else "-"
        self.sl_label = tk.Label(self, text=sl_text, bg=bg,
                                  fg=self.colors.text_primary, font=font, width=10)
        self.sl_label.pack(side=tk.LEFT, padx=2)

        # TP Label (display only)
        tp_value = position.get("take_profit", 0) or 0
        tp_text = f"{tp_value:.5f}" if tp_value else "-"
        self.tp_label = tk.Label(self, text=tp_text, bg=bg,
                                  fg=self.colors.text_primary, font=font, width=10)
        self.tp_label.pack(side=tk.LEFT, padx=2)

        # Edit button
        tk.Button(self, text="Edit", command=self._on_edit_click, bg=self.colors.bg_input,
                  fg=self.colors.text_primary, relief=tk.FLAT, font=("Helvetica", 9),
                  padx=8, cursor="hand2").pack(side=tk.LEFT, padx=2)

        # Close button
        tk.Button(self, text="X", command=self._on_close_click, bg=self.colors.btn_close_bg,
                  fg=self.colors.text_primary, relief=tk.FLAT, font=("Helvetica", 9, "bold"),
                  width=2, cursor="hand2").pack(side=tk.LEFT, padx=2)

    def _on_edit_click(self) -> None:
        """Open the position modify dialog."""
        dialog = PositionModifyDialog(
            self.winfo_toplevel(),
            self.position,
            colors=self.colors,
            on_apply=self._on_dialog_apply,
        )
        dialog.wait_window()

    def _on_dialog_apply(self, ticket: int, sl: float, tp: float,
                         trailing_enabled: bool, trailing_percent: float) -> None:
        """Handle dialog apply callback."""
        # Call modify callback for SL/TP changes
        if self.on_modify:
            self.on_modify(ticket, sl, tp)

        # Call trailing toggle callback if trailing was enabled
        if self.on_trailing_toggle and trailing_enabled:
            self.on_trailing_toggle(ticket, trailing_enabled, trailing_percent)

    def _on_close_click(self):
        if self.on_close:
            self.on_close(self.ticket)

    def update_profit(self, profit: float):
        pl_color = self.colors.text_profit_positive if profit >= 0 else self.colors.text_profit_negative
        self.profit_label.config(text=f"${profit:+.2f}", fg=pl_color)

    def update_sl_tp(self, sl: float, tp: float):
        """Update displayed SL/TP values."""
        sl_text = f"{sl:.5f}" if sl else "-"
        tp_text = f"{tp:.5f}" if tp else "-"
        self.sl_label.config(text=sl_text)
        self.tp_label.config(text=tp_text)
        # Also update position dict for next dialog open
        self.position["stop_loss"] = sl
        self.position["take_profit"] = tp

    def get_sl(self) -> float:
        return self.position.get("stop_loss", 0) or 0.0

    def get_tp(self) -> float:
        return self.position.get("take_profit", 0) or 0.0


class PositionsPanel(tk.Frame):
    """Scrollable panel showing all open positions."""

    def __init__(
        self,
        parent,
        colors: Colors = DEFAULT_COLORS,
        on_modify: Optional[Callable[[int, float, float], None]] = None,
        on_close: Optional[Callable[[int], None]] = None,
        on_trailing_toggle: Optional[Callable[[int, bool, float], None]] = None,
        on_refresh: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(parent, bg=colors.bg_main, **kwargs)
        self.colors = colors
        self.on_modify = on_modify
        self.on_close = on_close
        self.on_trailing_toggle = on_trailing_toggle
        self.on_refresh = on_refresh
        self._rows: dict[int, PositionRow] = {}

        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=self.colors.bg_status)
        header.pack(fill=tk.X, pady=(0, 2))

        tk.Label(header, text="OPEN POSITIONS", bg=self.colors.bg_status,
                 fg=self.colors.text_primary, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)

        self.count_label = tk.Label(header, text="(0)", bg=self.colors.bg_status,
                                    fg=self.colors.text_secondary, font=("Helvetica", 10))
        self.count_label.pack(side=tk.LEFT)

        tk.Button(header, text="Refresh", command=self._on_refresh_click, bg=self.colors.bg_input,
                  fg=self.colors.text_primary, relief=tk.FLAT, font=("Helvetica", 9)).pack(side=tk.RIGHT, padx=5)

        # Column headers
        col_header = tk.Frame(self, bg=self.colors.bg_status)
        col_header.pack(fill=tk.X)
        for text, width in [("Symbol", 8), ("Type", 5), ("Vol", 5), ("Entry", 8),
                            ("P/L", 8), ("SL", 10), ("TP", 10), ("", 6), ("", 3)]:
            tk.Label(col_header, text=text, bg=self.colors.bg_status, fg=self.colors.text_secondary,
                     font=("Helvetica", 8), width=width).pack(side=tk.LEFT, padx=2)

        # Scrollable content
        self.canvas = tk.Canvas(self, bg=self.colors.bg_main, highlightthickness=0, height=150)
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.content = tk.Frame(self.canvas, bg=self.colors.bg_main)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.create_window((0, 0), window=self.content, anchor=tk.NW)
        self.content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def _on_refresh_click(self):
        if self.on_refresh:
            self.on_refresh()

    def update_positions(self, positions: list[dict]):
        # Clear existing
        for widget in self.content.winfo_children():
            widget.destroy()
        self._rows.clear()

        # Add rows
        for i, pos in enumerate(positions):
            row = PositionRow(
                self.content, pos, self.colors,
                on_modify=self.on_modify,
                on_close=self.on_close,
                on_trailing_toggle=self.on_trailing_toggle,
            )
            row.pack(fill=tk.X, pady=1)
            self._rows[pos.get("ticket", i)] = row

        self.count_label.config(text=f"({len(positions)})")

    def update_position_profit(self, ticket: int, profit: float):
        if ticket in self._rows:
            self._rows[ticket].update_profit(profit)

    def clear(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        self._rows.clear()
        self.count_label.config(text="(0)")
