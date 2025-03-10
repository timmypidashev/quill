from typing import Dict, Any, Optional

class Item:
    """
    Represents an item in the game world.
    """
    
    def __init__(self, item_id: str, data: Dict[str, Any]):
        """
        Initialize an item from YAML data.
        
        Args:
            item_id: Unique identifier for the item
            data: Parsed YAML data for the item
        """
        self.id = item_id
        self.data = data
        self.name = data.get("name", item_id)
        self.description = data.get("description", "")
        self.takeable = data.get("takeable", True)
        self.weight = data.get("weight", 0.0)
        self.examination = data.get("examination", {})
        self.effects = data.get("effects", {})
    
    def get_name(self) -> str:
        """Get the display name of the item."""
        return self.name
    
    def get_description(self) -> str:
        """Get the short description of the item."""
        return self.description
    
    def get_examination_text(self) -> str:
        """Get the detailed examination text for the item."""
        if isinstance(self.examination, dict) and "text" in self.examination:
            return self.examination["text"]
        
        if isinstance(self.examination, str):
            return self.examination
        
        return self.description
    
    def get_effect(self, effect_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific effect for the item.
        
        Args:
            effect_key: Key for the effect (e.g., "use", "use_on_door")
            
        Returns:
            Effect data dictionary or None if not found
        """
        if not self.effects:
            return None
            
        return self.effects.get(effect_key)
    
    def is_takeable(self) -> bool:
        """Check if the item can be picked up."""
        return self.takeable
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access to item data."""
        if key in self.data:
            return self.data[key]
        
        raise KeyError(f"Item has no attribute '{key}'")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like get method for item data."""
        return self.data.get(key, default)
