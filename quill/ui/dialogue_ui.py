import sys
import time
from typing import List, Dict, Any, Optional

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class DummyFore:
        def __getattr__(self, name):
            return ""
    class DummyBack:
        def __getattr__(self, name):
            return ""
    class DummyStyle:
        def __getattr__(self, name):
            return ""
    Fore = DummyFore()
    Back = DummyBack()
    Style = DummyStyle()

class DialogueMenu:
    """
    Handles dialogue menu display and interaction.
    """
    
    def __init__(self, width: int = 70):
        """
        Initialize the dialogue menu.
        
        Args:
            width: Width of the dialogue box in characters
        """
        self.width = width
        
        # Check if running in interactive mode
        self.interactive = sys.stdout.isatty()
    
    def show_dialogue(self, character_name: str, text: str, options: List[Dict[str, Any]]):
        """
        Display a dialogue with options.
        
        Args:
            character_name: Name of the character speaking
            text: Dialogue text
            options: List of response options
        """
        # Print character name and dialogue
        self._print_dialogue_box(character_name, text)
        
        # Print response options
        if HAS_COLOR:
            print(Fore.CYAN + "\nYour response:")
            for i, option in enumerate(options):
                print(f"{Fore.CYAN + Style.BRIGHT}{i+1}. {Style.RESET_ALL}{option['text']}")
        else:
            print("\nYour response:")
            for i, option in enumerate(options):
                print(f"{i+1}. {option['text']}")
    
    def get_choice(self) -> Optional[int]:
        """
        Get the player's dialogue choice.
        
        Returns:
            Index of chosen option or None if invalid
        """
        try:
            choice = input("> ")
            if not choice.strip():
                return None
                
            choice_num = int(choice)
            if choice_num < 1:
                print("Invalid choice.")
                return None
                
            # Return zero-based index
            return choice_num - 1
            
        except ValueError:
            print("Please enter a number.")
            return None
    
    def _print_dialogue_box(self, character_name: str, text: str):
        """
        Print a styled dialogue box.
        
        Args:
            character_name: Name of the character speaking
            text: Dialogue text
        """
        # Split text into lines to fit width
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > self.width - 4:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Print the dialogue box
        print()
        if HAS_COLOR:
            # Character name header
            name_padding = max(0, self.width - len(character_name) - 4)
            print(f"{Fore.MAGENTA + Style.BRIGHT}╔═ {character_name} {'═' * name_padding}╗")
            
            # Dialogue text
            for line in lines:
                padding = max(0, self.width - len(line) - 4)
                print(f"{Fore.MAGENTA}║ {Fore.WHITE}{line}{' ' * padding}{Fore.MAGENTA} ║")
            
            # Bottom of box
            print(f"{Fore.MAGENTA + Style.BRIGHT}╚{'═' * (self.width - 2)}╝")
        else:
            # Simple version without colors
            name_padding = max(0, self.width - len(character_name) - 4)
            print(f"+- {character_name} {'-' * name_padding}+")
            
            for line in lines:
                padding = max(0, self.width - len(line) - 4)
                print(f"| {line}{' ' * padding} |")
            
            print(f"+{'-' * (self.width - 2)}+")
