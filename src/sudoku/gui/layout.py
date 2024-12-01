"""
Layout management for the Sudoku GUI.
"""
import tkinter as tk
from typing import List, Optional, Tuple


def configure_grid(
    widget: tk.Widget,
    rows: int,
    cols: int,
    weights: Optional[Tuple[List[int], List[int]]] = None,
) -> None:
    """Configure grid weights for rows and columns."""
    row_weights, col_weights = weights or ([1] * rows, [1] * cols)

    for i, weight in enumerate(row_weights):
        widget.grid_rowconfigure(i, weight=weight)
    for i, weight in enumerate(col_weights):
        widget.grid_columnconfigure(i, weight=weight)
