"""
Main GUI application class for the Sudoku game.
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import time
import random
import numpy as np
from typing import List, Dict, Set, Optional, Tuple, Any, Callable

from ..core import (
    solve_sudoku, count_solutions,
    find_conflicts, generate_puzzle
)
from ..ai import SudokuAI
from .widgets import (
    CellWidget, ControlPanel, DifficultySelector, StatusBar,
    CellPosition
)
from .styles import GUI_STYLES
from .layout import configure_grid

class SudokuGame:
    """Game state management for Sudoku."""
    
    def __init__(self):
        self.board = np.zeros((9, 9), dtype=np.uint8)
        self.original = np.zeros((9, 9), dtype=np.uint8)
        self.solution = np.zeros((9, 9), dtype=np.uint8)
        self.mistakes = 0
        self.undo_stack: List[np.ndarray] = []
        self.redo_stack: List[np.ndarray] = []
        self.MAX_STACK_SIZE = 100
        
    def set_value(self, row: int, col: int, value: int) -> bool:
        """Set a value in the board."""
        if self.original[row, col] != 0:
            return False
            
        if 0 <= value <= 9:
            self.save_state()
            self.board[row, col] = value
            return True
        return False
    
    def save_state(self) -> None:
        """Save current state to undo stack."""
        if len(self.undo_stack) >= self.MAX_STACK_SIZE:
            self.undo_stack.pop(0)
        self.undo_stack.append(self.board.copy())
        self.redo_stack.clear()
        
    def can_undo(self) -> bool:
        return bool(self.undo_stack)
        
    def can_redo(self) -> bool:
        return bool(self.redo_stack)
        
    def undo(self) -> Optional[np.ndarray]:
        """Undo last move."""
        if self.can_undo():
            self.redo_stack.append(self.board.copy())
            self.board = self.undo_stack.pop()
            return self.board
        return None
        
    def redo(self) -> Optional[np.ndarray]:
        """Redo last undone move."""
        if self.can_redo():
            self.undo_stack.append(self.board.copy())
            self.board = self.redo_stack.pop()
            return self.board
        return None
        
    def clear(self) -> None:
        """Clear the game state."""
        self.board.fill(0)
        self.original.fill(0)
        self.solution.fill(0)
        self.mistakes = 0
        self.undo_stack.clear()
        self.redo_stack.clear()

class GameTimer:
    """Manages game timing."""
    
    def __init__(self, master: tk.Tk, callback: Callable[[int, int], None]):
        self.master = master
        self.start_time: Optional[float] = None
        self.running = False
        self.callback = callback
        self._timer_id: Optional[str] = None
        
    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.time()
        self.running = True
        self._update()
        
    def stop(self) -> None:
        """Stop the timer."""
        self.running = False
        if self._timer_id:
            self.master.after_cancel(self._timer_id)
            self._timer_id = None
            
    def _update(self) -> None:
        """Update timer display."""
        if self.running and self.start_time:
            elapsed = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed, 60)
            self.callback(minutes, seconds)
            self._timer_id = self.master.after(1000, self._update)

class SudokuGUI:
    """GUI for the Sudoku Solver with Advanced AI."""

    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Sudoku Solver with Advanced AI")
        self.master.configure(bg=GUI_STYLES['colors']['background'])

        # Initialize components
        self.game = SudokuGame()
        self.cells: List[List[CellWidget]] = []
        self.show_ai_steps = tk.BooleanVar(value=True)
        
        # Create UI layout
        self._setup_layout()
        self._create_board()
        self._create_controls()
        
        # Initialize timer
        self.timer = GameTimer(self.master, self.status_bar.update_timer)
        
        # Configure event bindings
        self._setup_event_bindings()

    def _setup_layout(self) -> None:
        """Configure the main window layout."""
        weights = (
            [3, 1, 1, 1, 1],  # Row weights
            [1]               # Column weights
        )
        configure_grid(self.master, len(weights[0]), len(weights[1]), weights)

    def _create_board(self) -> None:
        """Create the Sudoku board grid."""
        board_frame = tk.Frame(self.master, bg=GUI_STYLES['colors']['border'])
        board_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        configure_grid(board_frame, 9, 9, ([1] * 9, [1] * 9))
        
        self.cells = []
        for row in range(9):
            row_cells = []
            for col in range(9):
                position = CellPosition.from_position(row, col)
                cell = CellWidget(
                    board_frame,
                    position,
                    {
                        'on_focus': self._on_cell_focus,
                        'on_change': self._on_cell_change
                    }
                )
                cell.grid(row=row, column=col, sticky='nsew')
                row_cells.append(cell)
            self.cells.append(row_cells)

    def _create_controls(self) -> None:
        """Create control panels and status displays."""
        # Control panel
        self.control_panel = ControlPanel(
            self.master,
            {
                'generate': self.generate_puzzle_gui,
                'import': self.import_puzzle,
                'solve': self.solve_puzzle,
                'ai_solve': self.ai_solve_puzzle,
                'hint': self.give_hint,
                'undo': self.undo_move,
                'redo': self.redo_move,
                'clear': self.clear_board
            }
        )
        self.control_panel.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        
        # Difficulty selector
        self.difficulty_selector = DifficultySelector(self.master)
        self.difficulty_selector.grid(row=2, column=0, pady=5, padx=10, sticky='ew')
        
        # Status bar
        self.status_bar = StatusBar(self.master)
        self.status_bar.grid(row=3, column=0, pady=5, padx=10, sticky='ew')
        
        # AI steps checkbox
        ai_steps_frame = tk.Frame(
            self.master,
            bg=GUI_STYLES['colors']['background']
        )
        ai_steps_frame.grid(row=4, column=0, pady=5, padx=10, sticky='w')
        
        tk.Checkbutton(
            ai_steps_frame,
            text="Show AI Steps",
            variable=self.show_ai_steps,
            font=GUI_STYLES['fonts']['label'],
            bg=GUI_STYLES['colors']['background']
        ).pack()

    def _setup_event_bindings(self) -> None:
        """Setup global event bindings."""
        self.master.bind('<Control-z>', lambda e: self.undo_move())
        self.master.bind('<Control-y>', lambda e: self.redo_move())
        self.master.bind('<Control-n>', lambda e: self.generate_puzzle_gui())
        
    def _on_cell_focus(self, row: int, col: int) -> None:
        """Handle cell focus event."""
        self._highlight_related_cells(row, col)
        if not self.timer.running:
            self.timer.start()

    def _on_cell_change(self, row: int, col: int) -> None:
        """Handle cell value change event."""
        cell = self.cells[row][col]
        value = cell.get().strip()
        
        try:
            num = int(value) if value else 0
            if 0 <= num <= 9:
                if self.game.set_value(row, col, num):
                    self._update_game_state()
            else:
                cell.set_value('')
        except ValueError:
            cell.set_value('')

    def _update_game_state(self) -> None:
        """Update game state and display."""
        conflicts = find_conflicts(self.game.board)
        self._update_cell_colors(conflicts)
        
        if conflicts:
            self.status_bar.update_status(
                "Invalid placements detected!",
                GUI_STYLES['colors']['error']
            )
            self.game.mistakes += 1
        else:
            self._check_solution_state()

    def _update_cell_colors(self, conflicts: Set[Tuple[int, int]]) -> None:
        """Update cell colors based on conflicts."""
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                if (row, col) in conflicts:
                    cell.config(fg=GUI_STYLES['colors']['error'])
                else:
                    cell.config(
                        fg=GUI_STYLES['colors']['readonly']
                        if cell.readonly
                        else GUI_STYLES['colors']['cell_text']
                    )

    def _check_solution_state(self) -> None:
        """Check and update the current solution state."""
        filled_cells = np.count_nonzero(self.game.board)
        empty_cells = 81 - filled_cells
        solution_count = count_solutions(self.game.board.copy(), limit=3)
        
        status_text = {
            0: ("The Sudoku board is not solvable.", GUI_STYLES['colors']['error']),
            1: ("The Sudoku board has a unique solution.", GUI_STYLES['colors']['success']),
            2: ("The Sudoku board has multiple solutions.", GUI_STYLES['colors']['warning'])
        }.get(min(solution_count, 2))
        
        if status_text:
            self.status_bar.update_status(*status_text)
            
        self.status_bar.update_analysis(
            f"Filled cells: {filled_cells}, Empty cells: {empty_cells}, "
            f"Mistakes: {self.game.mistakes}"
        )
    def solve_puzzle(self) -> None:
        """Solve the current puzzle."""
        self.status_bar.update_status("Solving puzzle...")
        self.master.update_idletasks()
        
        conflicts = find_conflicts(self.game.board)
        if conflicts:
            messagebox.showerror(
                "Error",
                "Cannot solve the puzzle due to invalid placements."
            )
            return

        solution_count = count_solutions(self.game.board.copy(), limit=2)
        if solution_count == 0:
            messagebox.showinfo("No Solution", "The Sudoku puzzle is unsolvable.")
        elif solution_count > 1:
            messagebox.showinfo(
                "Multiple Solutions",
                "The Sudoku puzzle has multiple solutions."
            )
        else:
            board_copy = self.game.board.copy()
            if solve_sudoku(board_copy):
                self._display_solution(board_copy)
            else:
                messagebox.showinfo(
                    "No Solution",
                    "The Sudoku puzzle is unsolvable."
                )

    def ai_solve_puzzle(self) -> None:
        """Solve the puzzle using AI strategies."""
        self.status_bar.update_status("AI solving puzzle...")
        self.master.update_idletasks()

        conflicts = find_conflicts(self.game.board)
        if conflicts:
            messagebox.showerror(
                "Error",
                "Cannot solve the puzzle due to invalid placements."
            )
            return

        ai_solver = SudokuAI(self.game.board.copy())
        if ai_solver.solve():
            if self.show_ai_steps.get():
                self._display_ai_solution(ai_solver)
            else:
                self._display_solution(ai_solver.board)
                self.status_bar.update_status(
                    "Puzzle solved using AI!",
                    GUI_STYLES['colors']['success']
                )
        else:
            messagebox.showinfo(
                "No Solution",
                "The Sudoku puzzle is unsolvable."
            )

    def _display_solution(self, solution: np.ndarray) -> None:
        """Display the solution on the board."""
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                if not cell.readonly:
                    value = str(solution[row, col])
                    cell.set_value(value, GUI_STYLES['colors']['success'])
                    self.game.board[row, col] = solution[row, col]

        self.status_bar.update_status(
            "Puzzle solved!",
            GUI_STYLES['colors']['success']
        )
        self.timer.stop()

    def _display_ai_solution(self, ai_solver: SudokuAI) -> None:
        """Display AI solution steps."""
        self.solution_steps = ai_solver.steps
        self.current_step = 0
        self._show_next_ai_step()

    def _show_next_ai_step(self) -> None:
        """Show the next AI solution step."""
        if self.current_step < len(self.solution_steps):
            row, col, num, technique = self.solution_steps[self.current_step]
            
            cell = self.cells[row][col]
            cell.set_value(str(num), GUI_STYLES['colors']['success'])
            self.game.board[row, col] = num
            
            self.status_bar.update_status(
                f"Step {self.current_step + 1}: {technique} at ({row + 1}, {col + 1})",
                GUI_STYLES['colors']['success']
            )
            
            self.current_step += 1
            self.master.after(200, self._show_next_ai_step)
        else:
            self.status_bar.update_status(
                "Puzzle solved using AI!",
                GUI_STYLES['colors']['success']
            )
            self.timer.stop()

    def generate_puzzle_gui(self) -> None:
        """Generate a new puzzle."""
        self.clear_board()
        
        difficulty_map = {1: 'Easy', 2: 'Medium', 3: 'Hard'}
        selected_difficulty = difficulty_map[self.difficulty_selector.slider.get()]
        
        self.status_bar.update_status(
            f"Generating {selected_difficulty} puzzle..."
        )
        self.master.update_idletasks()
        
        # Generate new puzzle
        self.game.board = generate_puzzle(selected_difficulty)
        self.game.original = self.game.board.copy()
        self.game.solution = self.game.board.copy()
        solve_sudoku(self.game.solution)
        
        self._display_puzzle()

    def _display_puzzle(self) -> None:
        """Display the current puzzle on the board."""
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                cell.set_value('')  # Clear cell
                
                num = self.game.board[row, col]
                if num != 0:
                    cell.set_value(str(num))
                    cell.readonly = True
                else:
                    cell.readonly = False

        self.status_bar.update_status("Puzzle generated.")
        self._update_game_state()
        self.timer.start()

    def import_puzzle(self) -> None:
        """Import a puzzle from a file."""
        file_path = filedialog.askopenfilename(
            title="Select Puzzle File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        
        if not file_path:
            return
            
        try:
            self._load_puzzle_from_file(file_path)
            self.status_bar.update_status("Puzzle imported successfully.")
            self._update_game_state()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import puzzle: {e}")

    def _load_puzzle_from_file(self, file_path: str) -> None:
        """Load puzzle from file with validation."""
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) != 9:
                raise ValueError("Invalid number of lines in file.")
                
            self.clear_board()
            
            for row, line in enumerate(lines):
                self._process_puzzle_line(row, line.strip())

    def _process_puzzle_line(self, row: int, line: str) -> None:
        """Process a single line of the puzzle file."""
        values = line.split() if ' ' in line else list(line)
        
        if len(values) != 9:
            raise ValueError(f"Invalid number of values in line {row + 1}.")
            
        for col, val in enumerate(values):
            cell = self.cells[row][col]
            cell.set_value('')
            
            if val in '0.':
                cell.readonly = False
                self.game.board[row, col] = 0
                self.game.original[row, col] = 0
            else:
                try:
                    num = int(val)
                    if not (1 <= num <= 9):
                        raise ValueError
                    cell.set_value(str(num))
                    cell.readonly = True
                    self.game.board[row, col] = num
                    self.game.original[row, col] = num
                except ValueError:
                    raise ValueError(
                        f"Invalid number '{val}' at row {row + 1}, column {col + 1}."
                    )

    def give_hint(self) -> None:
        """Provide a hint by filling in a random empty cell."""
        empty_cells = [
            (r, c) for r in range(9) for c in range(9)
            if self.game.board[r, c] == 0
        ]
        
        if not empty_cells:
            messagebox.showinfo(
                "No Empty Cells",
                "There are no empty cells to provide a hint."
            )
            return
            
        row, col = random.choice(empty_cells)
        if self.game.solution[row, col] != 0:
            value = str(self.game.solution[row, col])
            self.cells[row][col].set_value(value, GUI_STYLES['colors']['success'])
            self.game.board[row, col] = self.game.solution[row, col]
            self.game.save_state()

    def undo_move(self) -> None:
        """Undo the last move."""
        if board := self.game.undo():
            self._update_display_from_board(board)
            self._update_game_state()

    def redo_move(self) -> None:
        """Redo the last undone move."""
        if board := self.game.redo():
            self._update_display_from_board(board)
            self._update_game_state()

    def _update_display_from_board(self, board: np.ndarray) -> None:
        """Update cell display from board state."""
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                if not cell.readonly:
                    value = board[row, col]
                    cell.set_value(str(value) if value != 0 else '')

    def clear_board(self) -> None:
        """Clear the board state."""
        self.game.clear()
        self.timer.stop()
        
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                cell.set_value('')
                cell.readonly = False
                cell.config(bg=GUI_STYLES['colors']['cell_bg'])
                
        self.status_bar.update_status("Board cleared.")
        self.status_bar.update_analysis("")
        self.status_bar.update_timer(0, 0)

    def mainloop(self) -> None:
        """Start the main event loop."""
        self.master.mainloop()

    def cleanup(self) -> None:
        """Clean up resources before closing."""
        self.timer.stop()