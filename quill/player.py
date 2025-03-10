from typing import Set, List, Dict, Any

class Player:
    """
    Represents the player's state in the game.
    """
    
    def __init__(self):
        """Initialize a new player state."""
        self.inventory = []
        self.flags = set()
        self.quests = {}
        self.stats = {}
    
    def add_item(self, item_id: str) -> None:
        """
        Add an item to the player's inventory.
        
        Args:
            item_id: ID of the item to add
        """
        if item_id not in self.inventory:
            self.inventory.append(item_id)
    
    def remove_item(self, item_id: str) -> bool:
        """
        Remove an item from the player's inventory.
        
        Args:
            item_id: ID of the item to remove
            
        Returns:
            True if the item was removed, False if not found
        """
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            return True
        return False
    
    def has_item(self, item_id: str) -> bool:
        """
        Check if the player has a specific item.
        
        Args:
            item_id: ID of the item to check
            
        Returns:
            True if the item is in inventory
        """
        return item_id in self.inventory
    
    def get_inventory(self) -> List[str]:
        """
        Get the player's inventory.
        
        Returns:
            List of item IDs in inventory
        """
        return self.inventory.copy()
    
    def add_flag(self, flag: str) -> None:
        """
        Add a flag to the player's state.
        
        Args:
            flag: Flag to add
        """
        self.flags.add(flag)
    
    def remove_flag(self, flag: str) -> None:
        """
        Remove a flag from the player's state.
        
        Args:
            flag: Flag to remove
        """
        if flag in self.flags:
            self.flags.remove(flag)
    
    def has_flag(self, flag: str) -> bool:
        """
        Check if the player has a specific flag.
        
        Args:
            flag: Flag to check
            
        Returns:
            True if the flag is set
        """
        return flag in self.flags
    
    def get_flags(self) -> Set[str]:
        """
        Get all player flags.
        
        Returns:
            Set of all flags
        """
        return self.flags.copy()
    
    def start_quest(self, quest_id: str, quest_data: Dict[str, Any]) -> None:
        """
        Start a new quest.
        
        Args:
            quest_id: ID of the quest
            quest_data: Quest data including title, description, etc.
        """
        if quest_id not in self.quests:
            self.quests[quest_id] = {
                "title": quest_data.get("title", quest_id),
                "description": quest_data.get("description", ""),
                "objectives": quest_data.get("objectives", []),
                "completed": False,
                "progress": {}
            }
    
    def update_quest_progress(self, quest_id: str, objective_id: str, value: Any = True) -> None:
        """
        Update progress on a quest objective.
        
        Args:
            quest_id: ID of the quest
            objective_id: ID of the objective
            value: Progress value (True for completion, or numeric for partial progress)
        """
        if quest_id in self.quests:
            if "progress" not in self.quests[quest_id]:
                self.quests[quest_id]["progress"] = {}
            
            self.quests[quest_id]["progress"][objective_id] = value
    
    def complete_quest(self, quest_id: str) -> None:
        """
        Mark a quest as completed.
        
        Args:
            quest_id: ID of the quest
        """
        if quest_id in self.quests:
            self.quests[quest_id]["completed"] = True
    
    def get_active_quests(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active (non-completed) quests.
        
        Returns:
            Dictionary of quest ID to quest data
        """
        return {
            quest_id: quest_data
            for quest_id, quest_data in self.quests.items()
            if not quest_data.get("completed", False)
        }
    
    def get_completed_quests(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all completed quests.
        
        Returns:
            Dictionary of quest ID to quest data
        """
        return {
            quest_id: quest_data
            for quest_id, quest_data in self.quests.items()
            if quest_data.get("completed", False)
        }
    
    def set_stat(self, stat_name: str, value: Any) -> None:
        """
        Set a player statistic.
        
        Args:
            stat_name: Name of the stat
            value: Value to set
        """
        self.stats[stat_name] = value
    
    def get_stat(self, stat_name: str, default: Any = None) -> Any:
        """
        Get a player statistic.
        
        Args:
            stat_name: Name of the stat
            default: Default value if stat not found
            
        Returns:
            Stat value or default
        """
        return self.stats.get(stat_name, default)
