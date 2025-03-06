# soliloquy/character.py
from typing import Dict, List, Set, Any, Optional

class Character:
    """
    Represents a character in the game world.
    """
    
    def __init__(self, char_id: str, data: Dict[str, Any]):
        """
        Initialize a character from YAML data.
        
        Args:
            char_id: Unique identifier for the character
            data: Parsed YAML data for the character
        """
        self.id = char_id
        self.data = data
        self.name = data.get("name", char_id)
        self.description = data.get("description", "")
        self.dialogue = data.get("dialogue", {})
        self.dialogue_states = data.get("dialogue_states", {})
    
    def get_name(self) -> str:
        """Get the display name of the character."""
        return self.name
    
    def get_description(self) -> str:
        """Get the description of the character."""
        return self.description
    
    def get_dialogue(self, player_flags: Set[str]) -> Dict[str, Any]:
        """
        Get the appropriate dialogue based on character state.
        
        Args:
            player_flags: Set of player flags
            
        Returns:
            Dialogue data dictionary with text and options
        """
        # Check if any states apply based on flags
        for state_id, state_data in self.dialogue_states.items():
            if self._check_condition(state_data.get("condition", {}), player_flags):
                return {
                    "text": state_data.get("text", ""),
                    "options": state_data.get("options", [])
                }
        
        # Default dialogue
        return {
            "text": self.dialogue.get("text", ""),
            "options": self.dialogue.get("options", [])
        }
    
    def _check_condition(self, condition: Dict[str, Any], player_flags: Set[str]) -> bool:
        """
        Check if a condition is met based on player flags.
        
        Args:
            condition: Condition dictionary
            player_flags: Set of player flags
            
        Returns:
            True if condition is met
        """
        if not condition:
            return True
            
        # Required flags
        has_flags = set(condition.get("has_flags", []))
        if has_flags and not has_flags.issubset(player_flags):
            return False
            
        # Forbidden flags
        lacks_flags = set(condition.get("lacks_flags", []))
        if lacks_flags and lacks_flags.intersection(player_flags):
            return False
            
        return True
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access to character data."""
        if key in self.data:
            return self.data[key]
        
        raise KeyError(f"Character has no attribute '{key}'")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like get method for character data."""
        return self.data.get(key, default)
