# src/sudoku/gui/widgets.py
"""
Enhanced widget components for the Sudoku GUI with better organization and less redundancy.
"""
import tkinter as tk
from typing import Callable, Optional, Dict, List, Tuple
from dataclasses import dataclass
from .styles import GUI_STYLES

@dataclass
class CellPosition:
    """Represents a cell's position and border properties."""
    row: int
    col: int
    borders: Dict[str, int]

    @classmethod
    def from_position(cls, row: int, col: int) -> 'CellPosition':
        """Create a CellPosition with calculated border widths."""
        return cls(
            row=row,
            col=col,
            borders={
                'top': GUI_STYLES['dimensions']['border_thick'] if row % 3 == 0 else GUI_STYLES['dimensions']['border_thin'],
                'left': GUI_STYLES['dimensions']['border_thick'] if col % 3 == 0 else GUI_STYLES['dimensions']['border_thin'],
                'right': GUI_STYLES['dimensions']['border_thick'] if col % 3 == 2 else GUI_STYLES['dimensions']['border_thin'],
                'bottom': GUI_STYLES['dimensions']['border_thick'] if row % 3 == 2 else GUI_STYLES['dimensions']['border_thin']
            }
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
            self.config(bg=GUI_STYLES['colors']['highlight'] if is_hover else GUI_STYLES['colors']['cell_bg'])

class CellWidget(EnhancedEntry):
    """Enhanced Sudoku cell widget with improved functionality."""
    
    def __init__(self, master, position: CellPosition, callbacks: Dict[str, Callable]):
        super().__init__(
            master,
            width=GUI_STYLES['dimensions']['cell_width'],
            font=GUI_STYLES['fonts']['cell'],
            justify='center',
            relief='flat',
            bg=GUI_STYLES['colors']['cell_bg'],
            fg=GUI_STYLES['colors']['cell_text']
        )
        
        self.position = position
        self._readonly = False
        self._setup_bindings(callbacks)
        
    def _setup_bindings(self, callbacks: Dict[str, Callable]) -> None:
        """Setup event bindings with callbacks."""
        if 'on_focus' in callbacks:
            self.bind("<FocusIn>", 
                     lambda e: callbacks['on_focus'](self.position.row, self.position.col))
        if 'on_change' in callbacks:
            self.bind("<KeyRelease>", 
                     lambda e: callbacks['on_change'](self.position.row, self.position.col))
            
    @property
    def readonly(self) -> bool:
        return self._readonly
    
    @readonly.setter
    def readonly(self, value: bool) -> None:
        self._readonly = value
        self.config(fg=GUI_STYLES['colors']['readonly'] if value else GUI_STYLES['colors']['cell_text'])
        
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
            font=GUI_STYLES['fonts']['button'],
            bg=GUI_STYLES['colors']['button_bg'],
            fg='white',
            activebackground=GUI_STYLES['colors']['button_hover'],
            activeforeground='white',
            relief='flat',
            borderwidth=0,
            **kwargs
        )
        self._setup_hover_effect()
        
    def _setup_hover_effect(self) -> None:
        """Setup hover effect for the button."""
        self.bind("<Enter>", lambda e: self.config(bg=GUI_STYLES['colors']['button_hover']))
        self.bind("<Leave>", lambda e: self.config(bg=GUI_STYLES['colors']['button_bg']))

class ControlPanel(tk.Frame):
    """Reorganized control panel with improved button management."""
    
    def __init__(self, master, commands: Dict[str, Callable]):
        super().__init__(master, bg=GUI_STYLES['colors']['background'])
        self.buttons: List[Tuple[str, str]] = [
            ("Generate", 'generate'),
            ("Import", 'import'),
            ("Solve", 'solve'),
            ("AI Solve", 'ai_solve'),
            ("Hint", 'hint'),
            ("Undo", 'undo'),
            ("Redo", 'redo'),
            ("Clear", 'clear')
        ]
        self._create_buttons(commands)
        
    def _create_buttons(self, commands: Dict[str, Callable]) -> None:
        """Create and layout buttons with consistent styling."""
        for i, (text, command_key) in enumerate(self.buttons):
            self.grid_columnconfigure(i, weight=1)
            if command_key in commands:
                btn = EnhancedButton(self, text=text, command=commands[command_key])
                btn.grid(row=0, column=i, sticky='nsew', padx=2, pady=2)

class StatusBar(tk.Frame):
    """Enhanced status bar with improved label management."""
    
    def __init__(self, master):
        super().__init__(master, bg=GUI_STYLES['colors']['background'])
        self._create_labels()
        
    def _create_labels(self) -> None:
        """Create status labels with consistent styling."""
        self.labels = {
            'status': self._create_label("Enter numbers to start."),
            'analysis': self._create_label(""),
            'timer': self._create_label("Time: 00:00")
        }
        
    def _create_label(self, text: str) -> tk.Label:
        """Create a consistently styled label."""
        label = tk.Label(
            self,
            text=text,
            font=GUI_STYLES['fonts']['label'],
            bg=GUI_STYLES['colors']['background']
        )
        label.pack(pady=2)
        return label
        
    def update_status(self, text: str, color: Optional[str] = None) -> None:
        """Update status text with optional color."""
        self.labels['status'].config(text=text, fg=color or GUI_STYLES['colors']['cell_text'])
        
    def update_analysis(self, text: str) -> None:
        """Update analysis text."""
        self.labels['analysis'].config(text=text)
        
    def update_timer(self, minutes: int, seconds: int) -> None:
        """Update timer display."""
        self.labels['timer'].config(text=f"Time: {minutes:02d}:{seconds:02d}")

class DifficultySelector(tk.Frame):
    """Enhanced difficulty selector with improved slider management."""
    
    def __init__(self, master, on_change: Optional[Callable] = None):
        super().__init__(master, bg=GUI_STYLES['colors']['background'])
        self._create_widgets(on_change)
        
    def _create_widgets(self, on_change: Optional[Callable]) -> None:
        """Create selector widgets with consistent styling."""
        tk.Label(
            self,
            text="Difficulty:",
            font=GUI_STYLES['fonts']['label'],
            bg=GUI_STYLES['colors']['background']
        ).pack(side='left')
        
        self.slider = tk.Scale(
            self,
            from_=1,
            to=3,
            orient=tk.HORIZONTAL,
            label="Easy       Medium       Hard",
            showvalue=False,
            length=300,
            bg=GUI_STYLES['colors']['background'],
            highlightthickness=0,
            font=GUI_STYLES['fonts']['small'],
            command=on_change if on_change else lambda x: None
        )
        self.slider.pack(side='left')