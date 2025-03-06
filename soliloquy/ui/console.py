# soliloquy/ui/console.py
import os
import sys
import time
from typing import Dict, List, Any
import textwrap

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

class Console:
    """
    Handles console output formatting and styling.
    """
    
    def __init__(self, width: int = 80):
        """
        Initialize the console UI.
        
        Args:
            width: Width of the console output in characters
        """
        self.width = width
        self.wrapper = textwrap.TextWrapper(width=width, replace_whitespace=False)
    
    def clear(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_title(self, title: str):
        """
        Print a game title.
        
        Args:
            title: Game title
        """
        if HAS_COLOR:
            print(Fore.CYAN + Style.BRIGHT + "=" * self.width)
            print(Fore.CYAN + Style.BRIGHT + title.center(self.width))
            print(Fore.CYAN + Style.BRIGHT + "=" * self.width)
        else:
            print("=" * self.width)
            print(title.center(self.width))
            print("=" * self.width)
    
    def print_scene_title(self, title: str):
        """
        Print a scene title.
        
        Args:
            title: Scene title
        """
        print()
        if HAS_COLOR:
            print(Fore.YELLOW + Style.BRIGHT + title)
            print(Fore.YELLOW + Style.BRIGHT + "-" * len(title))
        else:
            print(title)
            print("-" * len(title))
    
    def print_info(self, message: str):
        """
        Print an info message.
        
        Args:
            message: Information message
        """
        if HAS_COLOR:
            wrapped = self.wrapper.fill(message)
            print(Fore.CYAN + wrapped)
        else:
            wrapped = self.wrapper.fill(message)
            print(wrapped)
    
    def print_error(self, message: str):
        """
        Print an error message.
        
        Args:
            message: Error message
        """
        if HAS_COLOR:
            print(Fore.RED + message)
        else:
            print("ERROR:", message)
    
    def print_description(self, description: str):
        """
        Print a scene description.
        
        Args:
            description: Scene description
        """
        wrapped = self.wrapper.fill(description)
        print(wrapped)
        print()
    
    def print_exits(self, exits: Dict[str, Any]):
        """
        Print available exits.
        
        Args:
            exits: Dictionary of exit name to exit data
        """
        if not exits:
            return
            
        if HAS_COLOR:
            print(Fore.GREEN + "Exits:")
            for exit_name, exit_data in exits.items():
                if isinstance(exit_data, dict) and "description" in exit_data:
                    print(f"  {Fore.GREEN + Style.BRIGHT}{exit_name}{Style.RESET_ALL}: {exit_data['description']}")
                else:
                    print(f"  {Fore.GREEN + Style.BRIGHT}{exit_name}")
        else:
            print("Exits:")
            for exit_name, exit_data in exits.items():
                if isinstance(exit_data, dict) and "description" in exit_data:
                    print(f"  {exit_name}: {exit_data['description']}")
                else:
                    print(f"  {exit_name}")
    
    def print_objects(self, objects: Dict[str, str]):
        """
        Print visible objects.
        
        Args:
            objects: Dictionary of object name to description
        """
        if not objects:
            return
            
        if HAS_COLOR:
            print(Fore.BLUE + "You can see:")
            for obj_name, obj_desc in objects.items():
                print(f"  {Fore.BLUE + Style.BRIGHT}{obj_name}")
        else:
            print("You can see:")
            for obj_name, obj_desc in objects.items():
                print(f"  {obj_name}")
    
    def print_characters(self, characters: Dict[str, Any]):
        """
        Print characters in the scene.
        
        Args:
            characters: Dictionary of character ID to character data
        """
        if not characters:
            return
            
        if HAS_COLOR:
            print(Fore.MAGENTA + "Characters:")
            for char_name, char_data in characters.items():
                name = char_data.get("name", char_name)
                print(f"  {Fore.MAGENTA + Style.BRIGHT}{name}")
        else:
            print("Characters:")
            for char_name, char_data in characters.items():
                name = char_data.get("name", char_name)
                print(f"  {name}")
    
    def print_items(self, items: List[str]):
        """
        Print a list of items with bullet points.
        
        Args:
            items: List of item names
        """
        if not items:
            return
            
        if HAS_COLOR:
            for item in items:
                print(f"  • {Fore.YELLOW}{item}")
        else:
            for item in items:
                print(f"  • {item}")
