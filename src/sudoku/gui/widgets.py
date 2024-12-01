"""
Enhanced widget components for the Sudoku GUI with centralized styling.
"""
import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from .styles import GUI_STYLES, get_color, get_font, get_spacing, get_theme_variant


@dataclass
class CellPosition:
    """Represents a cell's position and border properties."""

    row: int
    col: int
    borders: Dict[str, int]

    @classmethod
    def from_position(cls, row: int, col: int) -> "CellPosition":
        """Create a CellPosition with calculated border widths."""
        return cls(
            row=row,
            col=col,
            borders={
                "top": GUI_STYLES["dimensions"]["border_thick"]
                if row % 3 == 0
                else GUI_STYLES["dimensions"]["border_thin"],
                "left": GUI_STYLES["dimensions"]["border_thick"]
                if col % 3 == 0
                else GUI_STYLES["dimensions"]["border_thin"],
                "right": GUI_STYLES["dimensions"]["border_thick"]
                if col % 3 == 2
                else GUI_STYLES["dimensions"]["border_thin"],
                "bottom": GUI_STYLES["dimensions"]["border_thick"]
                if row % 3 == 2
                else GUI_STYLES["dimensions"]["border_thin"],
            },
        )


class EnhancedEntry(tk.Entry):
    """Base class for enhanced entry widgets with common functionality."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_hover_effect()

    def _setup_hover_effect(self) -> None:
        """Setup hover effect for the widget."""
        self.bind("<Enter>", lambda e: self._on_hover(True))
        self.bind("<Leave>", lambda e: self._on_hover(False))

    def _on_hover(self, is_hover: bool) -> None:
        """Handle hover state."""
        if self.focus_get() != self:
            self.config(
                bg=get_color("state.hover", "light")
                if is_hover
                else get_color("neutral", "surface")
            )


class CellWidget(EnhancedEntry):
    """Enhanced Sudoku cell widget with improved functionality."""

    def __init__(self, master, position: CellPosition, callbacks: Dict[str, Callable]):
        super().__init__(
            master,
            width=GUI_STYLES["dimensions"]["cell_width"],
            font=get_font("xl"),
            justify="center",
            relief="flat",
            bg=get_color("neutral", "surface"),
            fg=get_color("neutral.text", "primary"),
        )

        self.position = position
        self._readonly = False
        self._setup_bindings(callbacks)

    def _setup_bindings(self, callbacks: Dict[str, Callable]) -> None:
        """Setup event bindings with callbacks."""
        if "on_focus" in callbacks:
            self.bind(
                "<FocusIn>",
                lambda e: callbacks["on_focus"](self.position.row, self.position.col),
            )
        if "on_change" in callbacks:
            self.bind(
                "<KeyRelease>",
                lambda e: callbacks["on_change"](self.position.row, self.position.col),
            )

    @property
    def readonly(self) -> bool:
        return self._readonly

    @readonly.setter
    def readonly(self, value: bool) -> None:
        self._readonly = value
        self.config(
            fg=get_color("primary", "main")
            if value
            else get_color("neutral.text", "primary")
        )

    def set_value(self, value: str, color: Optional[str] = None) -> None:
        """Set cell value with optional color."""
        self.delete(0, tk.END)
        if value:
            self.insert(0, value)
            if color:
                self.config(fg=color)


class EnhancedButton(tk.Button):
    """Enhanced button with consistent styling and hover effects."""

    def __init__(self, master, text: str, command: Callable, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            font=get_font("md"),
            bg=get_color("primary", "main"),
            fg=get_color("primary", "contrast"),
            activebackground=get_color("primary", "dark"),
            activeforeground=get_color("primary", "contrast"),
            relief="flat",
            borderwidth=0,
            padx=get_spacing("md"),
            pady=get_spacing("sm"),
            **kwargs,
        )
        self._setup_hover_effect()

    def _setup_hover_effect(self) -> None:
        """Setup hover effect for the button."""
        self.bind("<Enter>", lambda e: self.config(bg=get_color("primary", "dark")))
        self.bind("<Leave>", lambda e: self.config(bg=get_color("primary", "main")))


class ControlPanel(tk.Frame):
    """Reorganized control panel with improved button management."""

    def __init__(self, master, commands: Dict[str, Callable]):
        super().__init__(master, bg=get_color("neutral", "background"))
        self.buttons: List[Tuple[str, str]] = [
            ("Generate", "generate"),
            ("Import", "import"),
            ("Solve", "solve"),
            ("AI Solve", "ai_solve"),
            ("Hint", "hint"),
            ("Undo", "undo"),
            ("Redo", "redo"),
            ("Clear", "clear"),
        ]
        self._create_buttons(commands)

    def _create_buttons(self, commands: Dict[str, Callable]) -> None:
        """Create and layout buttons with consistent styling."""
        for i, (text, command_key) in enumerate(self.buttons):
            self.grid_columnconfigure(i, weight=1)
            if command_key in commands:
                btn = EnhancedButton(self, text=text, command=commands[command_key])
                btn.grid(
                    row=0,
                    column=i,
                    sticky="nsew",
                    padx=get_spacing("xs"),
                    pady=get_spacing("xs"),
                )


class StatusBar(tk.Frame):
    """Enhanced status bar with improved label management."""

    def __init__(self, master):
        super().__init__(master, bg=get_color("neutral", "background"))
        self._create_labels()

    def _create_labels(self) -> None:
        """Create status labels with consistent styling."""
        self.labels = {
            "status": self._create_label("Enter numbers to start."),
            "analysis": self._create_label(""),
            "timer": self._create_label("Time: 00:00"),
        }

    def _create_label(self, text: str) -> tk.Label:
        """Create a consistently styled label."""
        label = tk.Label(
            self,
            text=text,
            font=get_font("md"),
            bg=get_color("neutral", "background"),
            fg=get_color("neutral.text", "primary"),
        )
        label.pack(pady=get_spacing("sm"))
        return label

    def update_status(self, text: str, color: Optional[str] = None) -> None:
        """Update status text with optional color."""
        self.labels["status"].config(
            text=text, fg=color or get_color("neutral.text", "primary")
        )

    def update_analysis(self, text: str) -> None:
        """Update analysis text."""
        self.labels["analysis"].config(text=text)

    def update_timer(self, minutes: int, seconds: int) -> None:
        """Update timer display."""
        self.labels["timer"].config(text=f"Time: {minutes:02d}:{seconds:02d}")


class DifficultySelector(tk.Frame):
    """Enhanced difficulty selector with improved slider management."""

    def __init__(self, master, on_change: Optional[Callable] = None):
        super().__init__(master, bg=get_color("neutral", "background"))
        self._create_widgets(on_change)

    def _create_widgets(self, on_change: Optional[Callable]) -> None:
        """Create selector widgets with consistent styling."""
        tk.Label(
            self,
            text="Difficulty:",
            font=get_font("md"),
            bg=get_color("neutral", "background"),
            fg=get_color("neutral.text", "primary"),
        ).pack(side="left", padx=get_spacing("md"))

        self.slider = tk.Scale(
            self,
            from_=1,
            to=3,
            orient=tk.HORIZONTAL,
            label="Easy       Medium       Hard",
            showvalue=False,
            length=300,
            bg=get_color("neutral", "background"),
            fg=get_color("neutral.text", "primary"),
            highlightthickness=0,
            font=get_font("sm"),
            command=on_change if on_change else lambda x: None,
        )
        self.slider.pack(side="left", padx=get_spacing("md"))
