import numpy as np
import random

def is_valid(board, row, col, num):
    """Check if placing num at board[row][col] is valid."""
    block_row, block_col = row // 3 * 3, col // 3 * 3
    if (num in board[row, :] or
        num in board[:, col] or
        num in board[block_row:block_row+3, block_col:block_col+3]):
        return False
    return True

def find_empty_cell(board):
    """Find an empty cell in the board."""
    empty_cells = np.argwhere(board == 0)
    return tuple(empty_cells[0]) if empty_cells.size else None

def solve_sudoku(board, numbers=None):
    """Solve the Sudoku board using backtracking."""
    if numbers is None:
        numbers = list(range(1, 10))
        random.shuffle(numbers)
    empty = find_empty_cell(board)
    if not empty:
        return True
    row, col = empty

    for num in numbers:
        if is_valid(board, row, col, num):
            board[row, col] = num
            if solve_sudoku(board, numbers):
                return True
            board[row, col] = 0  # Backtrack
    return False

def count_solutions(board, limit=2):
    """Count the number of solutions for the Sudoku board up to a limit."""
    count = [0]
    _count_solutions_helper(board, limit, count)
    return count[0]

def _count_solutions_helper(board, limit, count):
    """Helper function to count solutions with a limit."""
    if count[0] >= limit:
        return
    empty = find_empty_cell(board)
    if not empty:
        count[0] += 1
        return
    row, col = empty
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row, col] = num
            _count_solutions_helper(board, limit, count)
            board[row, col] = 0
            if count[0] >= limit:
                return

def find_conflicts(board):
    """Return a set of cells that have conflicts using numpy operations."""
    conflicts = set()
    # Rows and columns
    for i in range(9):
        row = board[i, :]
        duplicates = row[row > 0][np.unique(row[row > 0], return_counts=True)[1] > 1]
        for num in duplicates:
            indices = np.where(row == num)[0]
            conflicts.update({(i, idx) for idx in indices})

        col = board[:, i]
        duplicates = col[col > 0][np.unique(col[col > 0], return_counts=True)[1] > 1]
        for num in duplicates:
            indices = np.where(col == num)[0]
            conflicts.update({(idx, i) for idx in indices})

    # Blocks
    for br in range(3):
        for bc in range(3):
            block = board[br*3:(br+1)*3, bc*3:(bc+1)*3]
            unique, counts = np.unique(block[block > 0], return_counts=True)
            duplicates = unique[counts > 1]
            for num in duplicates:
                indices = np.argwhere(block == num)
                conflicts.update({(br*3 + idx[0], bc*3 + idx[1]) for idx in indices})
    return conflicts

def generate_puzzle(difficulty='Medium'):
    """Generate a random Sudoku puzzle with a unique solution."""
    board = np.zeros((9, 9), dtype=np.uint8)
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    solve_sudoku(board, numbers)  # Generate a random complete solution

    # Determine number of cells to remove based on difficulty
    difficulty_levels = {'Easy': 40, 'Medium': 50, 'Hard': 60}
    cells_to_remove = difficulty_levels.get(difficulty, 50)

    filled_positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(filled_positions)

    while cells_to_remove > 0 and filled_positions:
        row, col = filled_positions.pop()
        backup = board[row, col]
        board[row, col] = 0

        # Make a copy of the board to test for uniqueness
        board_copy = board.copy()
        solution_count = count_solutions(board_copy, limit=2)
        if solution_count != 1:
            board[row, col] = backup
        else:
            cells_to_remove -= 1
    return board
