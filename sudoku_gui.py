import tkinter as tk
from tkinter import messagebox, filedialog
import time
import random
import numpy as np
from sudoku_core import (
    is_valid, find_empty_cell, solve_sudoku, count_solutions,
    find_conflicts, generate_puzzle
)
from sudoku_ai import SudokuAI

class SudokuGUI:
    """GUI for the Sudoku Solver with Advanced AI."""

    def __init__(self, master):
        self.master = master
        master.title("Sudoku Solver with Advanced AI")

        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.puzzle = np.zeros((9, 9), dtype=np.uint8)
        self.solution = np.zeros((9, 9), dtype=np.uint8)
        self.undo_stack = []
        self.redo_stack = []
        self.mistakes = 0
        self.start_time = None
        self.timer_running = False
        self.create_widgets()
    def create_widgets(self):
        """Create the GUI widgets with enhanced styling and features."""
        # Set global theme and colors
        self.master.configure(bg='#f0f0f0')  # Light gray background

        # Enhanced entry fields with consistent borders and hover effects
        for row in range(9):
            for col in range(9):
                # Determine border widths
                top = 2 if row % 3 == 0 else 1
                left = 2 if col % 3 == 0 else 1
                right = 2 if col == 8 else 0
                bottom = 2 if row == 8 else 0

                cell_frame = tk.Frame(
                    self.master,
                    bg='black',
                    highlightbackground='black',
                    highlightcolor='black',
                    highlightthickness=0,
                    bd=0,
                    width=40,
                    height=40
                )
                cell_frame.grid(row=row, column=col, sticky='nsew')

                # Create an inner frame to act as the border
                inner_frame = tk.Frame(
                    cell_frame,
                    bg='black',
                    bd=0
                )
                inner_frame.pack(expand=True, fill='both', padx=(left, right), pady=(top, bottom))

                entry = tk.Entry(
                    inner_frame,
                    width=2,
                    font=("Segoe UI", 18),
                    justify='center',
                    relief='flat',
                    bg='#ffffff',  # White cell background
                    fg='#333333',  # Dark gray text
                )
                entry.pack(expand=True, fill='both')

                entry.bind("<FocusIn>", self.on_cell_focus)
                entry.bind("<KeyRelease>", self.on_key_release)

                # Add hover effect for cells
                entry.bind("<Enter>", lambda e, entry=entry: entry.config(bg='#e6e6e6'))
                entry.bind("<Leave>", lambda e, entry=entry: entry.config(bg='#ffffff'))

                self.cells[row][col] = entry

        # Configure row and column weights for dynamic resizing
        for i in range(9):
            self.master.grid_rowconfigure(i, weight=1)
            self.master.grid_columnconfigure(i, weight=1)

        # Buttons with hover effects
        button_frame = tk.Frame(self.master, bg='#f0f0f0')
        button_frame.grid(row=9, column=0, columnspan=9, pady=10, sticky='ew')

        buttons = [
            ("Generate", self.generate_puzzle_gui),
            ("Import", self.import_puzzle),
            ("Solve", self.solve_puzzle),
            ("AI Solve", self.ai_solve_puzzle),
            ("Hint", self.give_hint),
            ("Undo", self.undo_move),
            ("Redo", self.redo_move),
            ("Clear", self.clear_board),
        ]
        def style_button(btn):
            btn.config(
                font=("Segoe UI", 12),
                bg='#0078d4',  # Blue button background
                fg='white',  # White text
                activebackground='#005a9e',  # Darker blue on hover
                activeforeground='white',
                relief='flat',
                borderwidth=0,
            )
            btn.bind("<Enter>", lambda e: btn.config(bg='#005a9e'))
            btn.bind("<Leave>", lambda e: btn.config(bg='#0078d4'))

        # Configure column weights in the button_frame
        for i in range(len(buttons)):
            button_frame.grid_columnconfigure(i, weight=1)

        # Place buttons using grid
        for idx, (text, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command)
            style_button(btn)
            btn.grid(row=0, column=idx, sticky='nsew', padx=2, pady=2)

        difficulty_frame = tk.Frame(self.master, bg='#f0f0f0')
        difficulty_frame.grid(row=10, column=0, columnspan=9, pady=10)

        difficulty_label = tk.Label(difficulty_frame, text="Difficulty:", font=("Segoe UI", 12), bg="#f0f0f0")
        difficulty_label.pack(side='left')

        self.difficulty_slider = tk.Scale(
            difficulty_frame,
            from_=1,
            to=3,
            orient=tk.HORIZONTAL,
            label="Easy       Medium       Hard",
            showvalue=False,
            length=300,
            bg="#f0f0f0",
            highlightthickness=0,
            font=("Segoe UI", 10),
        )
        self.difficulty_slider.pack(side='left')

        # Add status label with enhanced font
        self.status_label = tk.Label(self.master, text="Enter numbers to start.", font=("Segoe UI", 12), bg='#f0f0f0')
        self.status_label.grid(row=11, column=0, columnspan=9, pady=5)

        # Analysis labels
        self.analysis_label = tk.Label(self.master, text="", font=("Segoe UI", 12), bg='#f0f0f0')
        self.analysis_label.grid(row=12, column=0, columnspan=9)

        self.timer_label = tk.Label(self.master, text="Time: 00:00", font=("Segoe UI", 12), bg='#f0f0f0')
        self.timer_label.grid(row=13, column=0, columnspan=9)

        # Add a checkbox for showing AI steps
        self.show_ai_steps = tk.BooleanVar(value=True)
        ai_steps_checkbox = tk.Checkbutton(
            self.master,
            text="Show AI Steps",
            variable=self.show_ai_steps,
            font=("Segoe UI", 12),
            bg='#f0f0f0',
        )
        ai_steps_checkbox.grid(row=14, column=0, columnspan=9)

        # Configure additional grid rows
        for i in range(9, 15):
            self.master.grid_rowconfigure(i, weight=0)

    def on_cell_focus(self, event):
        self.highlight_related_cells(event.widget)
        if not self.timer_running:
            self.start_timer()

    def highlight_related_cells(self, widget):
        """Highlight row, column, and box of the selected cell."""
        for row in range(9):
            for col in range(9):
                cell_bg = 'white'
                self.cells[row][col].config(bg=cell_bg)

        for row in range(9):
            for col in range(9):
                if self.cells[row][col] == widget:
                    # Highlight row and column
                    for i in range(9):
                        self.cells[row][i].config(bg='#e6f7ff')
                        self.cells[i][col].config(bg='#e6f7ff')
                    # Highlight 3x3 grid
                    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
                    for i in range(3):
                        for j in range(3):
                            self.cells[start_row + i][start_col + j].config(bg='#e6f7ff')
                    widget.config(bg='#cceeff')
                    return

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            self.timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}")
            self.master.after(1000, self.update_timer())

    def on_key_release(self, event):
        self.update_board()
        self.check_board()
        self.save_state()

    def update_board(self):
        self.board = np.zeros((9, 9), dtype=np.uint8)
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                val = cell.get()
                if val == '':
                    self.board[row, col] = 0
                    if not getattr(cell, 'readonly', False):
                        cell.config(fg='black')
                else:
                    try:
                        num = int(val)
                        if 1 <= num <= 9:
                            self.board[row, col] = num
                        else:
                            cell.delete(0, tk.END)
                            self.board[row, col] = 0
                    except ValueError:
                        cell.delete(0, tk.END)
                        self.board[row, col] = 0
                if getattr(cell, 'readonly', False):
                    cell.config(fg='blue')

    def check_board(self):
        self.update_board()
        conflicts = find_conflicts(self.board)
        # Update cell colors based on conflicts
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                if (row, col) in conflicts:
                    cell.config(fg='red')
                else:
                    if not getattr(cell, 'readonly', False):
                        cell.config(fg='black')
                    else:
                        cell.config(fg='blue')
        if conflicts:
            self.status_label.config(text="Invalid placements detected!", fg="red")
            self.mistakes += 1
        else:
            # Count filled and empty cells
            filled_cells = np.count_nonzero(self.board)
            empty_cells = 81 - filled_cells
            # Count solutions
            solution_count = count_solutions(self.board.copy(), limit=3)
            if solution_count == 0:
                self.status_label.config(
                    text="The Sudoku board is not solvable.", fg="red"
                )
            elif solution_count == 1:
                self.status_label.config(
                    text="The Sudoku board has a unique solution.", fg="green"
                )
                self.analysis_label.config(
                    text=f"Filled cells: {filled_cells}, Empty cells: {empty_cells}, Mistakes: {self.mistakes}"
                )
            else:
                self.status_label.config(
                    text="The Sudoku board has multiple solutions.", fg="orange"
                )
                self.analysis_label.config(
                    text=f"Filled cells: {filled_cells}, Empty cells: {empty_cells}, Mistakes: {self.mistakes}"
                )

    def save_state(self):
        self.undo_stack.append(self.get_current_state())
        self.redo_stack.clear()

    def get_current_state(self):
        state = []
        for row in range(9):
            current_row = []
            for col in range(9):
                cell = self.cells[row][col]
                val = cell.get()
                current_row.append(val)
            state.append(current_row)
        return state

    def solve_puzzle(self):
        self.status_label.config(text="Solving puzzle...", fg="black")
        self.master.update_idletasks()
        self._solve_puzzle_thread()

    def _solve_puzzle_thread(self):
        self.update_board()
        conflicts = find_conflicts(self.board)
        if conflicts:
            messagebox.showerror(
                "Error", "Cannot solve the puzzle due to invalid placements."
            )
            return
        solution_count = count_solutions(self.board.copy(), limit=2)
        if solution_count == 0:
            messagebox.showinfo(
                "No Solution", "The Sudoku puzzle is unsolvable."
            )
        elif solution_count > 1:
            messagebox.showinfo(
                "Multiple Solutions", "The Sudoku puzzle has multiple solutions."
            )
        else:
            # Solve and display the solution
            board_copy = self.board.copy()
            if solve_sudoku(board_copy):
                self._display_solution(board_copy)
            else:
                messagebox.showinfo(
                    "No Solution", "The Sudoku puzzle is unsolvable."
                )

    def _display_solution(self, solution):
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                if not getattr(cell, 'readonly', False):
                    cell.delete(0, tk.END)
                    cell.insert(0, str(solution[row, col]))
                    cell.config(fg='green')
        self.status_label.config(text="Puzzle solved!", fg="blue")
        self.timer_running = False

    def ai_solve_puzzle(self):
        self.status_label.config(text="AI solving puzzle...", fg="black")
        self.master.update_idletasks()
        self._ai_solve_puzzle_thread()

    def _ai_solve_puzzle_thread(self):
        self.update_board()
        conflicts = find_conflicts(self.board)
        if conflicts:
            messagebox.showerror(
                "Error", "Cannot solve the puzzle due to invalid placements."
            )
            return

        ai_solver = SudokuAI(self.board.copy())
        solved = ai_solver.solve()
        if solved:
            if self.show_ai_steps.get():
                self.display_ai_solution(ai_solver)
            else:
                self._display_solution(ai_solver.board)
                self.status_label.config(
                    text="Puzzle solved using AI!", fg="blue"
                )
                self.timer_running = False
        else:
            messagebox.showinfo(
                "No Solution", "The Sudoku puzzle is unsolvable."
            )

    def display_ai_solution(self, ai_solver):
        self.solution_steps = ai_solver.steps
        self.current_step = 0
        self.show_next_step()

    def show_next_step(self):
        if self.current_step < len(self.solution_steps):
            row, col, num, technique = self.solution_steps[self.current_step]
            cell = self.cells[row][col]
            cell.delete(0, tk.END)
            cell.insert(0, str(num))
            cell.config(fg='green')
            self.status_label.config(
                text=f"Step {self.current_step + 1}: {technique} at ({row + 1}, {col + 1})",
                fg="blue",
            )
            self.current_step += 1
            self.master.after(200, self.show_next_step)
        else:
            self.status_label.config(text="Puzzle solved using AI!", fg="blue")
            self.timer_running = False

    def generate_puzzle_gui(self):
        self.clear_board()
        difficulty_map = {1: 'Easy', 2: 'Medium', 3: 'Hard'}
        selected_difficulty = difficulty_map[self.difficulty_slider.get()]
        self.status_label.config(text=f"Generating {selected_difficulty} puzzle...", fg="black")
        self.master.update_idletasks()
        self._generate_puzzle_thread(selected_difficulty)

    def _generate_puzzle_thread(self, difficulty):
        self.puzzle = generate_puzzle(difficulty)
        self.solution = self.puzzle.copy()
        solve_sudoku(self.solution)
        self._display_puzzle()

    def _display_puzzle(self):
        for row in range(9):
            for col in range(9):
                num = self.puzzle[row, col]
                cell = self.cells[row][col]
                cell.delete(0, tk.END)
                cell_bg = 'white'
                cell.config(bg=cell_bg)
                if num != 0:
                    cell.insert(0, str(num))
                    cell.config(fg='blue')
                    cell.readonly = True
                else:
                    if hasattr(cell, 'readonly'):
                        del cell.readonly
        self.status_label.config(text="Puzzle generated.", fg="black")
        self.check_board()
        self.start_timer()

    def clear_board(self):
        self.timer_running = False
        self.mistakes = 0
        self.timer_label.config(text="Time: 00:00")
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                cell.delete(0, tk.END)
                cell.config(fg='black')
                cell_bg = 'white'
                cell.config(bg=cell_bg)
                if hasattr(cell, 'readonly'):
                    del cell.readonly
        self.status_label.config(text="Board cleared.", fg="black")
        self.analysis_label.config(text="")
        self.undo_stack.clear()
        self.redo_stack.clear()

    def import_puzzle(self):
        file_path = filedialog.askopenfilename(
            title="Select Puzzle File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")),
        )
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    if len(lines) != 9:
                        raise ValueError("Invalid number of lines in file.")
                    for row in range(9):
                        line = lines[row].strip()
                        values = line.split() if ' ' in line else list(line)
                        if len(values) != 9:
                            raise ValueError(
                                f"Invalid number of values in line {row + 1}."
                            )
                        for col in range(9):
                            val = values[col]
                            cell = self.cells[row][col]
                            cell.delete(0, tk.END)
                            if val in '0.':
                                if hasattr(cell, 'readonly'):
                                    del cell.readonly
                            else:
                                num = int(val)
                                if not (1 <= num <= 9):
                                    raise ValueError(
                                        f"Invalid number '{num}' at row {row + 1}, column {col + 1}."
                                    )
                                cell.insert(0, str(num))
                                cell.config(fg='blue')
                                cell.readonly = True
                    self.status_label.config(
                        text="Puzzle imported successfully.", fg="black"
                    )
                    self.check_board()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import puzzle: {e}")

    def give_hint(self):
        self.update_board()
        # Find an empty cell
        empty_cells = [
            (r, c) for r in range(9) for c in range(9) if self.cells[r][c].get() == ''
        ]
        if not empty_cells:
            messagebox.showinfo(
                "No Empty Cells", "There are no empty cells to provide a hint."
            )
            return
        row, col = random.choice(empty_cells)
        # Fill in the correct number
        if self.solution[row, col] != 0:
            self.cells[row][col].insert(0, str(self.solution[row, col]))
            self.cells[row][col].config(fg='green')
            self.save_state()

    def undo_move(self):
        if self.undo_stack:
            state = self.undo_stack.pop()
            self.redo_stack.append(self.get_current_state())
            self.set_board_state(state)
            self.check_board()

    def redo_move(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(self.get_current_state())
            self.set_board_state(state)
            self.check_board()

    def set_board_state(self, state):
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                cell.delete(0, tk.END)
                val = state[row][col]
                if val != '':
                    cell.insert(0, val)
                if getattr(cell, 'readonly', False):
                    cell.config(fg='blue')
                else:
                    cell.config(fg='black')
        self.update_board()

    def mainloop(self):
        self.master.mainloop()
