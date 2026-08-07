"""
Input Hook Manager - Advanced Screen Reader
FileName: core/hook_manager.py
Description: Low-level keyboard and mouse input listener for global hotkeys 
             and mouse click tracking using pynput.
"""

import logging
import threading
from typing import Callable, Dict, Optional
from pynput import keyboard, mouse

logger = logging.getLogger("ScreenReader")


class HookManager:
    """
    Manages global keyboard hotkeys and mouse listeners.
    Interprets shortcuts even when the screen reader application is minimized or in background.
    """

    def __init__(self):
        self._mouse_listener: Optional[mouse.Listener] = None
        self._global_hotkey_listener: Optional[keyboard.GlobalHotKeys] = None
        self._hotkey_callbacks: Dict[str, Callable[[], None]] = {}
        self._mouse_click_callback: Optional[Callable[[int, int], None]] = None
        self._is_running = False

    def register_hotkey(self, hotkey_str: str, callback: Callable[[], None]):
        """
        Registers a global hotkey string (e.g., '<ctrl>+<alt>+r') with its assigned callback function.
        """
        self._hotkey_callbacks[hotkey_str] = callback
        logger.debug(f"Registered global hotkey: {hotkey_str}")

    def set_mouse_click_callback(self, callback: Callable[[int, int], None]):
        """Registers a callback for global mouse click coordinates (x, y)."""
        self._mouse_click_callback = callback

    def _on_mouse_click(self, x: int, y: int, button, pressed: bool):
        """Internal callback for mouse click events."""
        if pressed and button == mouse.Button.left:
            logger.debug(f"Left mouse click detected at screen coordinates: ({x}, {y})")
            if self._mouse_click_callback:
                try:
                    self._mouse_click_callback(x, y)
                except Exception as e:
                    logger.error(f"Error in mouse click callback: {str(e)}")

    def start(self):
        """Starts background listeners for keyboard hotkeys and mouse tracking."""
        if self._is_running:
            return

        self._is_running = True

        # Initialize Global Hotkeys Listener if callbacks exist
        if self._hotkey_callbacks:
            try:
                self._global_hotkey_listener = keyboard.GlobalHotKeys(self._hotkey_callbacks)
                self._global_hotkey_listener.start()
                logger.info("Global Hotkeys listener started successfully.")
            except Exception as e:
                logger.error(f"Failed to start Global Hotkeys listener: {str(e)}")

        # Initialize Mouse Listener
        try:
            self._mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
            self._mouse_listener.start()
            logger.info("Global Mouse listener started successfully.")
        except Exception as e:
            logger.error(f"Failed to start Mouse listener: {str(e)}")

    def stop(self):
        """Safely stops active keyboard and mouse listeners."""
        if not self._is_running:
            return

        self._is_running = False

        if self._global_hotkey_listener and self._global_hotkey_listener.running:
            try:
                self._global_hotkey_listener.stop()
            except Exception as e:
                logger.error(f"Error stopping hotkey listener: {str(e)}")

        if self._mouse_listener and self._mouse_listener.running:
            try:
                self._mouse_listener.stop()
            except Exception as e:
                logger.error(f"Error stopping mouse listener: {str(e)}")

        logger.info("Global Input Hooks stopped successfully.")


if __name__ == "__main__":
    import time

    logging.basicConfig(level=logging.INFO)
    logger.info("Testing core/hook_manager.py standalone...")

    def test_read_shortcut():
        logger.info("[Hotkey Action] Ctrl+Alt+R Pressed: Triggering Screen Read!")

    hook_mgr = HookManager()
    
    # Register hotkey mapping
    hook_mgr.register_hotkey('<ctrl>+<alt>+r', test_read_shortcut)
    hook_mgr.start()

    logger.info("Listening for '<ctrl>+<alt>+r' for 3 seconds...")
    time.sleep(3)

    hook_mgr.stop()
    logger.info("HookManager module test execution complete.")
