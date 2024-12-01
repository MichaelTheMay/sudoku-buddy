"""Tests for core Sudoku functionality."""
import pytest
import numpy as np
from src.sudoku.core import solve_sudoku, find_conflicts, generate_puzzle

def test_find_conflicts_empty_board(empty_board):
    """Test that an empty board has no conflicts."""
    conflicts = find_conflicts(empty_board)
    assert len(conflicts) == 0

def test_find_conflicts_valid_board(valid_board):
    """Test that a valid board has no conflicts."""
    conflicts = find_conflicts(valid_board)
    assert len(conflicts) == 0

def test_find_conflicts_invalid_board(invalid_board):
    """Test that conflicts are correctly identified."""
    conflicts = find_conflicts(invalid_board)
    assert len(conflicts) > 0
    assert (0, 0) in conflicts
    assert (0, 1) in conflicts

def test_solve_sudoku_already_solved(solved_board):
    """Test solving an already solved board."""
    board_copy = solved_board.copy()
    result = solve_sudoku(board_copy)
    assert result
    np.testing.assert_array_equal(board_copy, solved_board)

def test_solve_sudoku_valid_board(valid_board):
    """Test solving a valid partially filled board."""
    result = solve_sudoku(valid_board)
    assert result
    assert find_conflicts(valid_board) == set()
    assert np.count_nonzero(valid_board) == 81  # Board should be full

def test_solve_sudoku_invalid_board(invalid_board):
    """Test that solving an invalid board returns False."""
    result = solve_sudoku(invalid_board.copy())
    assert not result

@pytest.mark.parametrize("difficulty", ["Easy", "Medium", "Hard"])
def test_generate_puzzle(difficulty):
    """Test puzzle generation for different difficulty levels."""
    board = generate_puzzle(difficulty)
    assert isinstance(board, np.ndarray)
    assert board.shape == (9, 9)
    assert find_conflicts(board) == set()
    # Verify the board is partially filled
    empty_count = np.count_nonzero(board == 0)
    filled_count = 81 - empty_count
    assert 0 < filled_count < 81