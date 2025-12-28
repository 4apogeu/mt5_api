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
    """Symbol dropdown selector."""

    def __init__(
        self,
        parent,
        symbols: tuple,
        default: str,
        on_change: Optional[Callable[[str], None]] = None,
        colors: Colors = DEFAULT_COLORS,
        **kwargs,
    ):
        super().__init__(parent, bg=colors.bg_main, **kwargs)
        self.colors = colors
        self.on_change = on_change

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
            state="readonly",
            width=10,
            font=("Helvetica", 11),
        )
        self.combo.pack(side=tk.LEFT)
        self.combo.bind("<<ComboboxSelected>>", self._on_select)

    def _on_select(self, event):
        if self.on_change:
            self.on_change(self.var.get())

    def get(self) -> str:
        return self.var.get()


class VolumeInput(tk.Frame):
    """Volume input with increment/decrement buttons."""

    def __init__(
        self,
        parent,
        default: float,
        step: float,
        min_val: float,
        max_val: float,
        colors: Colors = DEFAULT_COLORS,
        **kwargs,
    ):
        super().__init__(parent, bg=colors.bg_main, **kwargs)
        self.colors = colors
        self.step = step
        self.min_val = min_val
        self.max_val = max_val

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
            self.var.set(f"{self.min_val:.2f}")

    def _increment(self):
        try:
            val = float(self.var.get()) + self.step
            val = min(self.max_val, val)
            self.var.set(f"{val:.2f}")
        except ValueError:
            self.var.set(f"{self.min_val:.2f}")

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


class PositionRow(tk.Frame):
    """Single position row with editable SL/TP fields."""

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

        # SL Entry
        self.sl_var = tk.StringVar(value=str(position.get("stop_loss", 0) or ""))
        self.sl_entry = tk.Entry(self, textvariable=self.sl_var, width=8, justify=tk.CENTER,
                                  bg=self.colors.bg_input, fg=self.colors.text_primary, relief=tk.FLAT, font=font)
        self.sl_entry.pack(side=tk.LEFT, padx=2)
        self.sl_entry.bind("<Return>", self._on_sl_tp_change)

        # TP Entry
        self.tp_var = tk.StringVar(value=str(position.get("take_profit", 0) or ""))
        self.tp_entry = tk.Entry(self, textvariable=self.tp_var, width=8, justify=tk.CENTER,
                                  bg=self.colors.bg_input, fg=self.colors.text_primary, relief=tk.FLAT, font=font)
        self.tp_entry.pack(side=tk.LEFT, padx=2)
        self.tp_entry.bind("<Return>", self._on_sl_tp_change)

        # Trailing checkbox
        self.trailing_var = tk.BooleanVar(value=False)
        self.trailing_percent_var = tk.StringVar(value="1.0")
        trail_frame = tk.Frame(self, bg=bg)
        trail_frame.pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(trail_frame, variable=self.trailing_var, command=self._on_trailing_change,
                       bg=bg, selectcolor=self.colors.bg_input).pack(side=tk.LEFT)
        tk.Entry(trail_frame, textvariable=self.trailing_percent_var, width=4, justify=tk.CENTER,
                 bg=self.colors.bg_input, fg=self.colors.text_primary, relief=tk.FLAT, font=font).pack(side=tk.LEFT)
        tk.Label(trail_frame, text="%", bg=bg, fg=self.colors.text_secondary, font=font).pack(side=tk.LEFT)

        # Close button
        tk.Button(self, text="X", command=self._on_close_click, bg=self.colors.btn_close_bg,
                  fg=self.colors.text_primary, relief=tk.FLAT, font=("Helvetica", 9, "bold"),
                  width=2, cursor="hand2").pack(side=tk.LEFT, padx=2)

    def _on_sl_tp_change(self, event=None):
        if self.on_modify:
            self.on_modify(self.ticket, self.get_sl(), self.get_tp())

    def _on_trailing_change(self):
        if self.on_trailing_toggle:
            try:
                percent = float(self.trailing_percent_var.get())
            except ValueError:
                percent = 1.0
            self.on_trailing_toggle(self.ticket, self.trailing_var.get(), percent)

    def _on_close_click(self):
        if self.on_close:
            self.on_close(self.ticket)

    def update_profit(self, profit: float):
        pl_color = self.colors.text_profit_positive if profit >= 0 else self.colors.text_profit_negative
        self.profit_label.config(text=f"${profit:+.2f}", fg=pl_color)

    def update_sl_tp(self, sl: float, tp: float):
        self.sl_var.set(str(sl) if sl else "")
        self.tp_var.set(str(tp) if tp else "")

    def get_sl(self) -> float:
        try:
            return float(self.sl_var.get()) if self.sl_var.get() else 0.0
        except ValueError:
            return 0.0

    def get_tp(self) -> float:
        try:
            return float(self.tp_var.get()) if self.tp_var.get() else 0.0
        except ValueError:
            return 0.0


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
                            ("P/L", 8), ("SL", 8), ("TP", 8), ("Trail", 8), ("", 3)]:
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
