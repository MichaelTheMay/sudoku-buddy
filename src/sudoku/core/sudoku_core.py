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
    count = [0]
    def _count_solutions_helper(board):
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
                _count_solutions_helper(board)
                if count[0] >= limit:
                    return
                board[row, col] = 0
    _count_solutions_helper(board.copy())
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
    board = np.zeros((9, 9), dtype=np.uint8)
    numbers = np.random.permutation(9) + 1
    
    # Fill diagonal boxes first
    for i in range(0, 9, 3):
        box = numbers.reshape(3, 3)
        board[i:i+3, i:i+3] = box
        np.random.shuffle(numbers)
    
    solve_sudoku(board)  # Fill the rest
    
    cells_to_remove = {'Easy': 40, 'Medium': 50, 'Hard': 60}[difficulty]
    positions = np.random.permutation(81)
    
    for pos in positions[:cells_to_remove]:
        row, col = pos // 9, pos % 9
        temp = board[row, col]
        board[row, col] = 0
        
        if count_solutions(board.copy()) != 1:
            board[row, col] = temp
            
    return board