"""Game timer management."""
import time
import tkinter as tk
from typing import Callable, Optional, Union


class GameTimer:
    """Manages game timing with tkinter integration."""

    def __init__(
        self, master: Union[tk.Misc, tk.Widget], callback: Callable[[int, int], None]
    ):
        """
        Initialize timer.

        Args:
            master: Tkinter widget to use for timing (any widget with after() method)
            callback: Function to call with (minutes, seconds) on timer update
        """
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
        """Stop the timer and cleanup."""
        self.running = False
        if self._timer_id is not None:
            self.master.after_cancel(self._timer_id)
            self._timer_id = None

    def _update(self) -> None:
        """Update timer display."""
        if self.running and self.start_time:
            elapsed = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed, 60)
            self.callback(minutes, seconds)
            self._timer_id = self.master.after(1000, self._update)
