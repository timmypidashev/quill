# soliloquy/utils/spinner.py
import sys
import time
import threading
import itertools
from contextlib import contextmanager

class Spinner:
    """
    A loading spinner animation for the console.
    """
    
    def __init__(self, message: str = "Thinking", delay: float = 0.1):
        """
        Initialize the spinner.
        
        Args:
            message: Message to display next to the spinner
            delay: Delay between frames in seconds
        """
        self.message = message
        self.delay = delay
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_cycle = itertools.cycle(self.spinner_chars)
        self.running = False
        self.spinner_thread = None
        
        # Check if running in interactive mode
        self.interactive = sys.stdout.isatty()
    
    def _spin(self):
        """Spinner animation thread function."""
        while self.running:
            char = next(self.spinner_cycle)
            sys.stdout.write(f"\r{char} {self.message}... ")
            sys.stdout.flush()
            time.sleep(self.delay)
    
    def start(self, message: str = None):
        """
        Start the spinner animation.
        
        Args:
            message: Optional message to display (overrides default)
        """
        if not self.interactive:
            # In non-interactive mode, just print the message
            print(f"{message or self.message}...")
            return
        
        if message:
            self.message = message
            
        if not self.running:
            self.running = True
            self.spinner_thread = threading.Thread(target=self._spin)
            self.spinner_thread.daemon = True
            self.spinner_thread.start()
    
    def stop(self):
        """Stop the spinner animation."""
        if not self.interactive:
            return
            
        if self.running:
            self.running = False
            if self.spinner_thread:
                self.spinner_thread.join()
            
            # Clear the spinner line
            sys.stdout.write("\r" + " " * (len(self.message) + 12) + "\r")
            sys.stdout.flush()
    
    # Fixed context manager implementation
    def __enter__(self):
        """Context manager enter method."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method."""
        self.stop()
        return False  # Don't suppress exceptions
