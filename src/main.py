import tkinter as tk

from sudoku.gui import SudokuGUI


def main():
    root = tk.Tk()
    gui = SudokuGUI(root)
    gui.mainloop()


if __name__ == "__main__":
    main()
