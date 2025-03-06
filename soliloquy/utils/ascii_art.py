# soliloquy/utils/ascii_art.py
import sys
import time
from typing import Optional

try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class DummyFore:
        def __getattr__(self, name):
            return ""
    class DummyStyle:
        def __getattr__(self, name):
            return ""
    Fore = DummyFore()
    Style = DummyStyle()

def display_ascii_art(art: str, color: str = "CYAN", delay: Optional[float] = 0.01, animate: bool = True):
    """
    Display ASCII art with optional animation.
    
    Args:
        art: ASCII art string
        color: Color name to use if available (default: CYAN)
        delay: Delay between lines in seconds (None for no animation)
        animate: Whether to animate the display
    """
    # Get the color if available
    color_code = getattr(Fore, color, "") if HAS_COLOR else ""
    
    # Check if running in interactive mode
    interactive = sys.stdout.isatty()
    
    lines = art.split("\n")
    
    # Print with animation if requested and in interactive mode
    if animate and delay is not None and interactive:
        for line in lines:
            sys.stdout.write(f"{color_code}{line}\n")
            sys.stdout.flush()
            time.sleep(delay)
    else:
        # Print all at once otherwise
        for line in lines:
            print(f"{color_code}{line}")

def create_title_banner(text: str, border_char: str = "=", padding: int = 1):
    """
    Create a simple banner with the given text.
    
    Args:
        text: Text to display in the banner
        border_char: Character to use for the border
        padding: Number of spaces to pad around the text
        
    Returns:
        String containing the banner
    """
    text_length = len(text)
    total_width = text_length + padding * 2 + 2  # +2 for the border chars on each side
    
    top_border = border_char * total_width
    bottom_border = border_char * total_width
    
    middle_line = f"{border_char}{' ' * padding}{text}{' ' * padding}{border_char}"
    
    banner = f"{top_border}\n{middle_line}\n{bottom_border}"
    return banner
