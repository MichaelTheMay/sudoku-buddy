"""Common test fixtures and configuration."""
import pytest
import numpy as np
from typing import List, Tuple

@pytest.fixture
def empty_board() -> np.ndarray:
    """Create an empty 9x9 Sudoku board."""
    return np.zeros((9, 9), dtype=np.uint8)

@pytest.fixture
def valid_board() -> np.ndarray:
    """Create a valid, partially filled Sudoku board."""
    board = np.zeros((9, 9), dtype=np.uint8)
    # Add some valid numbers
    board[0, 0] = 5
    board[0, 1] = 3
    board[1, 4] = 9
    board[2, 7] = 6
    return board

@pytest.fixture
def invalid_board() -> np.ndarray:
    """Create an invalid Sudoku board with conflicts."""
    board = np.zeros((9, 9), dtype=np.uint8)
    # Add conflicting numbers in same row
    board[0, 0] = 5
    board[0, 1] = 5
    return board

@pytest.fixture
def solved_board() -> np.ndarray:
    """Create a completely solved valid Sudoku board."""
    return np.array([
        [5,3,4,6,7,8,9,1,2],
        [6,7,2,1,9,5,3,4,8],
        [1,9,8,3,4,2,5,6,7],
        [8,5,9,7,6,1,4,2,3],
        [4,2,6,8,5,3,7,9,1],
        [7,1,3,9,2,4,8,5,6],
        [9,6,1,5,3,7,2,8,4],
        [2,8,7,4,1,9,6,3,5],
        [3,4,5,2,8,6,1,7,9]
    ], dtype=np.uint8)