"""
Event Loop Manager - Advanced Screen Reader
FileName: core/event_loop.py
Description: Asynchronous, thread-safe event loop for queueing and dispatching 
             accessibility events, voice triggers, and UI updates.
"""

import queue
import threading
import time
import logging
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any, Optional

logger = logging.getLogger("ScreenReader")


class EventType(Enum):
    """Enumeration of event types handled by the screen reader system."""
    FOCUS_CHANGED = auto()
    TEXT_SELECTION = auto()
    KEY_PRESSED = auto()
    VOICE_COMMAND = auto()
    OCR_REQUESTED = auto()
    IMAGE_CAPTION_REQUESTED = auto()
    SYSTEM_SHUTDOWN = auto()


@dataclass
class Event:
    """Represents a discrete system event with optional metadata payload."""
    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class EventLoop:
    """
    Thread-safe event queue and dispatcher mechanism.
    Runs continuously on a dedicated background thread to process events sequentially.
    """

    def __init__(self):
        self._event_queue: queue.Queue[Event] = queue.Queue()
        self._handlers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._is_running = False
        self._thread: Optional[threading.Thread] = None

    def register_handler(self, event_type: EventType, handler: Callable[[Event], None]):
        """Registers a callback function for a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.debug(f"Registered handler for event: {event_type.name}")

    def unregister_handler(self, event_type: EventType, handler: Callable[[Event], None]):
        """Unregisters a callback function from a specific event type."""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    def post_event(self, event: Event):
        """Thread-safe method to push a new event into the queue."""
        if self._is_running:
            self._event_queue.put(event)

    def _process_queue(self):
        """Internal worker loop pulling and dispatching events sequentially."""
        while self._is_running:
            try:
                # Short timeout allows periodic checking of self._is_running
                event = self._event_queue.get(timeout=0.2)
                self._dispatch(event)
                self._event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing event loop queue: {str(e)}")

    def _dispatch(self, event: Event):
        """Dispatches an event to all subscriber callbacks."""
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in handler '{handler.__name__}' for {event.type.name}: {str(e)}")

    def start(self):
        """Starts the background event dispatcher thread."""
        if self._is_running:
            return

        self._is_running = True
        self._thread = threading.Thread(
            target=self._process_queue,
            name="EventLoopThread",
            daemon=True
        )
        self._thread.start()
        logger.info("Core EventLoop thread started.")

    def stop(self):
        """Gracefully stops event loop execution."""
        if not self._is_running:
            return

        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        logger.info("Core EventLoop thread stopped.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Testing core/event_loop.py standalone...")

    # Sample handler callback function
    def sample_focus_handler(event: Event):
        element_name = event.data.get("element_name", "Unknown")
        logger.info(f"[Focus Event Callback] Element focused: {element_name}")

    # Initialize and start event loop
    loop = EventLoop()
    loop.register_handler(EventType.FOCUS_CHANGED, sample_focus_handler)
    loop.start()

    # Emit test event
    loop.post_event(Event(
        type=EventType.FOCUS_CHANGED,
        data={"element_name": "Start Button", "x": 50, "y": 1080}
    ))

    time.sleep(0.5)
    loop.stop()
    logger.info("EventLoop module test execution completed.")
