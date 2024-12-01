import numpy as np

def find_empty_cell_with_fewest_possibilities(board, possibilities):
    """Find the empty cell with the fewest possibilities."""
    min_options = 10
    min_cell = None
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                bits = possibilities[row, col]
                options = bin(bits).count('1')
                if options < min_options:
                    min_options = options
                    min_cell = (row, col)
                    if min_options == 1:
                        return min_cell
    return min_cell

class SudokuAI:
    """Advanced AI solver that uses logical strategies and optimizations."""

    def __init__(self, board):
        self.board = board
        self.steps = []
        self.possibilities = np.full((9, 9), (1 << 9) - 1, dtype=int)
        self.update_possibilities()

    def solve(self):
        """Solve the puzzle and record steps."""
        while True:
            progress = self.naked_singles() or self.hidden_singles()
            if not progress:
                break
        if self.is_solved():
            return True
        else:
            return self.backtrack_solve()

    def update_possibilities(self, affected_cells=None):
        """Update possibilities based on current board state."""
        if affected_cells is None:
            # Initial computation
            for row in range(9):
                for col in range(9):
                    if self.board[row, col] == 0:
                        self.possibilities[row, col] = self.compute_cell_possibilities(row, col)
                    else:
                        self.possibilities[row, col] = 0
        else:
            for row, col in affected_cells:
                if self.board[row, col] == 0:
                    self.possibilities[row, col] = self.compute_cell_possibilities(row, col)
                else:
                    self.possibilities[row, col] = 0
    def compute_cell_possibilities(self, row, col):
        used = np.zeros(10, dtype=bool)
        used[self.board[row, :]] = True
        used[self.board[:, col]] = True
        box = self.board[row//3*3:(row//3+1)*3, col//3*3:(col//3+1)*3]
        used[box.flatten()] = True
        return sum(1 << (i - 1) for i in range(1, 10) if not used[i])
    def naked_singles(self):
        """Fill in cells where there's only one possible number."""
        progress = False
        singles = np.argwhere((self.possibilities != 0) & ((self.possibilities & (self.possibilities - 1)) == 0))
        for row, col in singles:
            bits = int(self.possibilities[row, col])
            num = bits.bit_length()
            self.board[row, col] = num
            self.steps.append((row, col, num, 'Naked Single'))
            affected_cells = self.get_affected_cells(row, col)
            self.update_possibilities(affected_cells)
            progress = True
        return progress

    def hidden_singles(self):
        """Find hidden singles in rows, columns, and boxes."""
        progress = False
        for idx in range(9):
            # Rows
            counts = {}
            for col in range(9):
                bits = int(self.possibilities[idx, col])
                for num in range(1, 10):
                    if bits & (1 << (num - 1)):
                        counts.setdefault(num, []).append((idx, col))
            for num, positions in counts.items():
                if len(positions) == 1:
                    row, col = positions[0]
                    self.board[row, col] = num
                    self.steps.append((row, col, num, 'Hidden Single in Row'))
                    affected_cells = self.get_affected_cells(row, col)
                    self.update_possibilities(affected_cells)
                    progress = True

            # Columns
            counts = {}
            for row in range(9):
                bits = int(self.possibilities[row, idx])
                for num in range(1, 10):
                    if bits & (1 << (num - 1)):
                        counts.setdefault(num, []).append((row, idx))
            for num, positions in counts.items():
                if len(positions) == 1:
                    row, col = positions[0]
                    self.board[row, col] = num
                    self.steps.append((row, col, num, 'Hidden Single in Column'))
                    affected_cells = self.get_affected_cells(row, col)
                    self.update_possibilities(affected_cells)
                    progress = True

            # Boxes
            counts = {}
            start_row, start_col = 3 * (idx // 3), 3 * (idx % 3)
            for i in range(3):
                for j in range(3):
                    row, col = start_row + i, start_col + j
                    bits = int(self.possibilities[row, col])
                    for num in range(1, 10):
                        if bits & (1 << (num - 1)):
                            counts.setdefault(num, []).append((row, col))
            for num, positions in counts.items():
                if len(positions) == 1:
                    row, col = positions[0]
                    self.board[row, col] = num
                    self.steps.append((row, col, num, 'Hidden Single in Box'))
                    affected_cells = self.get_affected_cells(row, col)
                    self.update_possibilities(affected_cells)
                    progress = True
        return progress

    def get_affected_cells(self, row, col):
        """Get cells affected by a change at (row, col)."""
        affected_cells = set()
        affected_cells.update({(row, i) for i in range(9)})
        affected_cells.update({(i, col) for i in range(9)})
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        affected_cells.update({(start_row + i, start_col + j) for i in range(3) for j in range(3)})
        return affected_cells

    def is_solved(self):
        """Check if the board is solved."""
        return np.all(self.board != 0)

    def backtrack_solve(self):
        """Backtracking with MRV heuristic."""
        if self.is_solved():
            return True
        self.update_possibilities()
        cell = find_empty_cell_with_fewest_possibilities(self.board, self.possibilities)
        if not cell:
            return False
        row, col = cell
        bits = int(self.possibilities[row, col])
        nums = [num for num in range(1, 10) if bits & (1 << (num - 1))]

        for num in nums:
            self.board[row, col] = num
            self.steps.append((row, col, num, 'Backtracking with MRV'))
            affected_cells = self.get_affected_cells(row, col)
            self.update_possibilities(affected_cells)
            if self.backtrack_solve():
                return True
            self.board[row, col] = 0
            self.update_possibilities(affected_cells)
        return False
