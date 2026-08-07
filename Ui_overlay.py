"""
UI Overlay Module - Advanced Screen Reader
FileName: ui_overlay.py
Description: Provides high-contrast visual indicators and focused element 
             bounding boxes on screen for low-vision users.
"""

import tkinter as tk
import threading
import logging
from typing import Optional

logger = logging.getLogger("ScreenReader")


class UIOverlay:
    """
    Manages a transparent, always-on-top visual highlight frame on screen.
    Runs on a dedicated Tkinter background thread to avoid blocking main execution.
    """

    def __init__(self, border_color: str = "red", border_thickness: int = 4):
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self._thread: Optional[threading.Thread] = None
        self._is_visible = False
        self._running = False

    def _setup_window(self):
        """Initializes the transparent Tkinter root window."""
        try:
            self.root = tk.Tk()
            self.root.title("Screen Reader Highlight")

            # Remove window borders, keep on top of all windows
            self.root.overrideredirect(True)
            self.root.wm_attributes("-topmost", True)

            # Set background key color for transparency on Windows
            transparent_color = "#000001"
            self.root.wm_attributes("-transparentcolor", transparent_color)
            self.root.config(bg=transparent_color)

            self.canvas = tk.Canvas(
                self.root,
                bg=transparent_color,
                highlightthickness=0
            )
            self.canvas.pack(fill=tk.BOTH, expand=True)

            # Initial geometry (hidden offscreen)
            self.root.geometry("1x1+0+0")
            self.root.withdraw()

            self._running = True
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error in UI Overlay Tkinter initialization: {str(e)}")

    def start(self):
        """Starts the visual overlay loop in a daemon thread."""
        if self._running:
            return
        self._thread = threading.Thread(
            target=self._setup_window, 
            name="UIOverlayThread", 
            daemon=True
        )
        self._thread.start()

    def draw_highlight(self, x: int, y: int, width: int, height: int):
        """
        Positions and resizes the highlight rectangle over target screen coordinates.
        """
        if not self.root or not self._running:
            return

        def _update():
            try:
                padding = self.border_thickness
                win_x = max(0, x - padding)
                win_y = max(0, y - padding)
                win_w = width + (padding * 2)
                win_h = height + (padding * 2)

                self.root.geometry(f"{win_w}x{win_h}+{win_x}+{win_y}")

                # Redraw focus border box
                self.canvas.delete("all")
                self.canvas.create_rectangle(
                    padding // 2,
                    padding // 2,
                    win_w - (padding // 2),
                    win_h - (padding // 2),
                    outline=self.border_color,
                    width=self.border_thickness
                )

                if not self._is_visible:
                    self.root.deiconify()
                    self._is_visible = True
            except Exception as e:
                logger.error(f"Failed to render highlight rectangle: {str(e)}")

        # Thread-safe execution call to Tkinter engine
        if self.root:
            self.root.after(0, _update)

    def hide_highlight(self):
        """Hides the highlight frame from the screen."""
        if not self.root or not self._running:
            return

        def _hide():
            try:
                self.root.withdraw()
                self._is_visible = False
            except Exception as e:
                logger.error(f"Failed to hide overlay frame: {str(e)}")

        if self.root:
            self.root.after(0, _hide)

    def set_color(self, color: str):
        """Updates the highlight box border color (e.g. 'yellow', 'green', '#FF00FF')."""
        self.border_color = color

    def stop(self):
        """Safely closes the transparent Tkinter window."""
        if self.root and self._running:
            self._running = False
            self.root.after(0, self.root.destroy)


if __name__ == "__main__":
    import time
    
    logging.basicConfig(level=logging.INFO)
    logger.info("Testing ui_overlay.py standalone...")

    overlay = UIOverlay(border_color="red", border_thickness=4)
    overlay.start()

    # Wait briefly for thread execution setup
    time.sleep(0.5)

    # Test visual box render
    overlay.draw_highlight(x=300, y=200, width=400, height=150)
    time.sleep(2)

    # Test color change and move
    overlay.set_color("yellow")
    overlay.draw_highlight(x=100, y=100, width=250, height=80)
    time.sleep(2)

    # Cleanup test execution
    overlay.hide_highlight()
    overlay.stop()
    logger.info("Overlay test execution complete.")
