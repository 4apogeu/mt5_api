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
