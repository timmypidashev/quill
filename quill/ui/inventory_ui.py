from typing import List, Dict, Any

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

class InventoryDisplay:
    """
    Handles inventory display and interaction.
    """
    
    def __init__(self, width: int = 60):
        """
        Initialize the inventory display.
        
        Args:
            width: Width of the inventory display in characters
        """
        self.width = width
    
    def show(self, items: List[str]):
        """
        Display player inventory.
        
        Args:
            items: List of item names in inventory
        """
        if not items:
            if HAS_COLOR:
                print(f"\n{Fore.YELLOW}Inventory: {Style.BRIGHT}Empty")
            else:
                print("\nInventory: Empty")
            return
        
        if HAS_COLOR:
            print(f"\n{Fore.YELLOW + Style.BRIGHT}┌{'─' * (self.width - 2)}┐")
            print(f"{Fore.YELLOW + Style.BRIGHT}│{' INVENTORY ':^{self.width - 2}}│")
            print(f"{Fore.YELLOW + Style.BRIGHT}├{'─' * (self.width - 2)}┤")
            
            for item in items:
                padding = self.width - len(item) - 4
                print(f"{Fore.YELLOW}│ {Fore.WHITE + Style.BRIGHT}• {item}{' ' * padding}{Fore.YELLOW}│")
            
            print(f"{Fore.YELLOW + Style.BRIGHT}└{'─' * (self.width - 2)}┘")
        else:
            print("\n+", "-" * (self.width - 2), "+", sep="")
            print("|", " INVENTORY ".center(self.width - 2), "|", sep="")
            print("+", "-" * (self.width - 2), "+", sep="")
            
            for item in items:
                padding = self.width - len(item) - 4
                print("| • ", item, " " * padding, "|", sep="")
            
            print("+", "-" * (self.width - 2), "+", sep="")
    
    def show_detailed(self, items: List[Dict[str, Any]]):
        """
        Display detailed inventory with item descriptions.
        
        Args:
            items: List of item dictionaries with 'name' and 'description' fields
        """
        if not items:
            if HAS_COLOR:
                print(f"\n{Fore.YELLOW}Inventory: {Style.BRIGHT}Empty")
            else:
                print("\nInventory: Empty")
            return
        
        if HAS_COLOR:
            print(f"\n{Fore.YELLOW + Style.BRIGHT}┌{'─' * (self.width - 2)}┐")
            print(f"{Fore.YELLOW + Style.BRIGHT}│{' INVENTORY ':^{self.width - 2}}│")
            print(f"{Fore.YELLOW + Style.BRIGHT}├{'─' * (self.width - 2)}┤")
            
            for item in items:
                name = item.get('name', 'Unknown item')
                desc = item.get('description', '')
                
                # Print item name
                padding = self.width - len(name) - 4
                print(f"{Fore.YELLOW}│ {Fore.WHITE + Style.BRIGHT}• {name}{' ' * padding}{Fore.YELLOW}│")
                
                # Print description if available
                if desc:
                    # Split description into lines
                    max_desc_width = self.width - 6  # Account for margins and indent
                    words = desc.split()
                    lines = []
                    current_line = []
                    current_length = 0
                    
                    for word in words:
                        if current_length + len(word) + 1 > max_desc_width:
                            lines.append(" ".join(current_line))
                            current_line = [word]
                            current_length = len(word)
                        else:
                            current_line.append(word)
                            current_length += len(word) + 1
                    
                    if current_line:
                        lines.append(" ".join(current_line))
                    
                    # Print each line of description
                    for line in lines:
                        padding = self.width - len(line) - 6
                        print(f"{Fore.YELLOW}│  {Fore.WHITE}{line}{' ' * padding}{Fore.YELLOW}│")
                
                # Separator between items
                print(f"{Fore.YELLOW}│{' ' * (self.width - 2)}│")
            
            print(f"{Fore.YELLOW + Style.BRIGHT}└{'─' * (self.width - 2)}┘")
        else:
            print("\n+", "-" * (self.width - 2), "+", sep="")
            print("|", " INVENTORY ".center(self.width - 2), "|", sep="")
            print("+", "-" * (self.width - 2), "+", sep="")
            
            for item in items:
                name = item.get('name', 'Unknown item')
                desc = item.get('description', '')
                
                # Print item name
                padding = self.width - len(name) - 4
                print("| • ", name, " " * padding, "|", sep="")
                
                # Print description if available
                if desc:
                    # Split description into lines
                    max_desc_width = self.width - 6  # Account for margins and indent
                    words = desc.split()
                    lines = []
                    current_line = []
                    current_length = 0
                    
                    for word in words:
                        if current_length + len(word) + 1 > max_desc_width:
                            lines.append(" ".join(current_line))
                            current_line = [word]
                            current_length = len(word)
                        else:
                            current_line.append(word)
                            current_length += len(word) + 1
                    
                    if current_line:
                        lines.append(" ".join(current_line))
                    
                    # Print each line of description
                    for line in lines:
                        padding = self.width - len(line) - 6
                        print("|  ", line, " " * padding, "|", sep="")
                
                # Separator between items
                print("|", " " * (self.width - 2), "|", sep="")
            
            print("+", "-" * (self.width - 2), "+", sep="")
