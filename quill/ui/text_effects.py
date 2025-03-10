import sys
import time
import random
from typing import Optional

class TypeWriter:
    """
    Simulates typing effect for text output.
    """
    
    def __init__(self, min_delay: float = 0.01, max_delay: float = 0.05, end_delay: float = 0.5):
        """
        Initialize the typewriter effect.
        
        Args:
            min_delay: Minimum delay between characters in seconds
            max_delay: Maximum delay between characters in seconds
            end_delay: Delay after finishing a sentence in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.end_delay = end_delay
        
        # Check if running in interactive mode
        self.interactive = sys.stdout.isatty()
    
    def print(self, text: str, end: str = "\n", speed: Optional[float] = None):
        """
        Print text with a typewriter effect.
        
        Args:
            text: Text to print
            end: String to print at end (default: newline)
            speed: Override typing speed multiplier (1.0 = normal)
        """
        if not self.interactive:
            # Non-interactive mode, just print normally
            print(text, end=end)
            return
        
        # Apply typewriter effect
        if speed is None:
            min_d = self.min_delay
            max_d = self.max_delay
        else:
            min_d = self.min_delay / speed
            max_d = self.max_delay / speed
        
        for i, char in enumerate(text):
            sys.stdout.write(char)
            sys.stdout.flush()
            
            # Delay varies based on character
            if char in ".!?":
                # Longer pause after sentence endings
                time.sleep(self.end_delay)
            elif char in ",;:":
                # Medium pause after punctuation
                time.sleep(max_d * 1.5)
            elif char in "\n":
                # Pause after newlines
                time.sleep(max_d * 2)
            else:
                # Random delay for other characters
                time.sleep(random.uniform(min_d, max_d))
                
        # Print the end character
        sys.stdout.write(end)
        sys.stdout.flush()

class FadeIn:
    """
    Creates a fade-in effect for text.
    """
    
    def __init__(self, steps: int = 5, delay: float = 0.05):
        """
        Initialize the fade-in effect.
        
        Args:
            steps: Number of fade steps
            delay: Delay between steps in seconds
        """
        self.steps = steps
        self.delay = delay
        
        # Check if running in interactive mode with color support
        try:
            import colorama
            self.has_color = sys.stdout.isatty()
        except ImportError:
            self.has_color = False
    
    def print(self, text: str):
        """
        Print text with a fade-in effect.
        
        Args:
            text: Text to print
        """
        if not self.has_color:
            # Fall back to normal printing if no color support
            print(text)
            return
        
        try:
            import colorama
            from colorama import Fore, Style
            
            # Perform fade-in effect
            for i in range(self.steps):
                # Calculate brightness percentage
                brightness = (i + 1) / self.steps
                
                # Clear line and print with current brightness
                sys.stdout.write("\r" + " " * len(text) + "\r")
                
                # Simulate brightness with ANSI color intensity
                if brightness < 0.3:
                    color = Fore.BLACK + Style.DIM
                elif brightness < 0.6:
                    color = Fore.WHITE + Style.DIM
                else:
                    color = Fore.WHITE + Style.NORMAL
                
                sys.stdout.write(f"{color}{text}{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(self.delay)
            
            # Final newline
            print()
            
        except Exception:
            # Fall back if anything goes wrong
            print(text)
