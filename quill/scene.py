from typing import Dict, List, Set, Optional, Any

class Scene:
    """
    Represents a scene in the game world.
    """
    
    def __init__(self, scene_id: str, data: Dict[str, Any]):
        """
        Initialize a scene from YAML data.
        
        Args:
            scene_id: Unique identifier for the scene
            data: Parsed YAML data for the scene
        """
        self.id = scene_id
        self.name = data.get("name", scene_id)
        self.description = data.get("description", "")
        self.exits = data.get("exits", {})
        self.objects = data.get("objects", {})
        self.items = data.get("items", {})
        self.characters = data.get("characters", {})
        self.states = data.get("states", {})
        self.locked_exits = data.get("locked_exits", {})
        self.locked_items = data.get("locked_items", {})
        self.events = data.get("events", {})
        
        # Track revealed hidden objects
        self.revealed_objects = set()
    
    def get_description(self, player_flags: Set[str]) -> str:
        """
        Get the appropriate description based on scene state.
        
        Args:
            player_flags: Set of player flags
            
        Returns:
            Scene description
        """
        # Check if any states apply based on flags
        for state_id, state_data in self.states.items():
            if self._check_condition(state_data.get("condition", {}), player_flags):
                return state_data.get("description", self.description)
        
        return self.description
    
    def get_visible_exits(self, player_flags: Set[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get all visible exits for the current state.
        
        Args:
            player_flags: Set of player flags
            
        Returns:
            Dictionary of exit name to exit data
        """
        visible_exits = {}
        
        for exit_name, exit_data in self.exits.items():
            # Skip hidden exits unless they've been revealed
            if isinstance(exit_data, dict) and exit_data.get("hidden", False) and exit_name not in self.revealed_objects:
                continue
            
            # Handle simple string exits (legacy format)
            if isinstance(exit_data, str):
                visible_exits[exit_name] = {"target": exit_data, "description": f"Exit to {exit_name}"}
            else:
                visible_exits[exit_name] = exit_data
        
        return visible_exits
    
    def get_visible_objects(self, player_flags: Set[str]) -> Dict[str, str]:
        """
        Get all visible objects in the scene.
        
        Args:
            player_flags: Set of player flags
            
        Returns:
            Dictionary of object name to description
        """
        visible_objects = {}
        
        for obj_name, obj_data in self.objects.items():
            # Skip hidden objects unless they've been revealed
            if isinstance(obj_data, dict):
                if obj_data.get("hidden", False) and obj_name not in self.revealed_objects:
                    continue
                visible_objects[obj_name] = obj_data.get("description", "")
            else:
                # Handle simple string descriptions (legacy format)
                visible_objects[obj_name] = obj_data
        
        return visible_objects
    
    def has_object(self, object_name: str) -> bool:
        """Check if scene has a specific object."""
        return object_name in self.objects
    
    def get_object_description(self, object_name: str, player_flags: Set[str]) -> str:
        """Get the description for an object."""
        obj_data = self.objects.get(object_name)
        
        if not obj_data:
            return ""
            
        if isinstance(obj_data, dict):
            return obj_data.get("description", "")
        
        return obj_data
    
    def reveal_hidden_objects(self, object_name: str, player) -> None:
        """
        Reveal any hidden objects associated with examining this object.
        
        Args:
            object_name: The object being examined
            player: Player object for updating flags
        """
        obj_data = self.objects.get(object_name)
        
        if not obj_data or not isinstance(obj_data, dict):
            return
            
        # Check if examining this object reveals others
        reveals = obj_data.get("reveals", [])
        for revealed_obj in reveals:
            self.revealed_objects.add(revealed_obj)
            
        # Set any flags from examining
        if "flags_set" in obj_data:
            for flag in obj_data["flags_set"]:
                player.add_flag(flag)
    
    def find_item(self, item_name: str) -> Optional[str]:
        """
        Find item ID by name in the scene.
        
        Args:
            item_name: Name of the item to find
            
        Returns:
            Item ID if found, None otherwise
        """
        # Direct ID match first
        if item_name in self.items:
            return item_name
            
        # Check for items with a matching name property
        for item_id, item_data in self.items.items():
            if isinstance(item_data, dict) and item_data.get("name", "").lower() == item_name.lower():
                return item_id
        
        return None
    
    def remove_item(self, item_id: str) -> None:
        """Remove an item from the scene."""
        if item_id in self.items:
            del self.items[item_id]
    
    def is_exit_locked(self, exit_name: str, player_flags: Set[str]) -> bool:
        """Check if an exit is locked based on player flags."""
        if exit_name not in self.locked_exits:
            return False
            
        lock_data = self.locked_exits[exit_name]
        return self._check_condition(lock_data.get("condition", {}), player_flags)
    
    def get_locked_exit_message(self, exit_name: str) -> str:
        """Get the message for a locked exit."""
        if exit_name not in self.locked_exits:
            return f"You can't go that way."
            
        return self.locked_exits[exit_name].get("message", "That way is locked.")
    
    def is_item_locked(self, item_id: str, player_flags: Set[str]) -> bool:
        """Check if an item is locked based on player flags."""
        if item_id not in self.locked_items:
            return False
            
        lock_data = self.locked_items[item_id]
        return self._check_condition(lock_data.get("condition", {}), player_flags)
    
    def get_locked_item_message(self, item_id: str) -> str:
        """Get the message for a locked item."""
        if item_id not in self.locked_items:
            return f"You can't take that."
            
        return self.locked_items[item_id].get("message", "You can't take that right now.")
    
    def check_event(self, trigger: str, player_flags: Set[str]) -> Optional[Dict[str, Any]]:
        """
        Check if the given trigger activates any events.
        
        Args:
            trigger: Event trigger string
            player_flags: Set of player flags
            
        Returns:
            Event data if triggered, None otherwise
        """
        for event_id, event_data in self.events.items():
            event_trigger = event_data.get("trigger", "").lower()
            
            # Check for matching trigger and conditions
            if event_trigger == trigger.lower() and self._check_condition(event_data.get("condition", {}), player_flags):
                return event_data
        
        return None
    
    def has_character(self, character_id: str, player_flags: Set[str]) -> bool:
        """
        Check if a character is present in this scene.
        
        Args:
            character_id: Character ID to check
            player_flags: Player flags for conditional presence
            
        Returns:
            True if character is present
        """
        # Simple presence check (legacy format)
        if character_id in self.characters and isinstance(self.characters[character_id], bool):
            return self.characters[character_id]
            
        # Complex presence with conditions
        if character_id in self.characters and isinstance(self.characters[character_id], dict):
            char_data = self.characters[character_id]
            
            # Check presence condition if specified
            if "condition" in char_data:
                return self._check_condition(char_data["condition"], player_flags)
            
            # Default to True if character is listed without condition
            return True
        
        return False
    
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
