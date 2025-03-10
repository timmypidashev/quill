import os
import glob
import yaml
from typing import Dict, List, Any
import logging
import traceback

from .scene import Scene
from .item import Item
from .character import Character

class GameLoader:
    """
    Handles loading and parsing game files.
    """
    
    def __init__(self, game_dir: str = None):
        """
        Initialize the game loader.
        
        Args:
            game_dir: Directory containing game YAML files.
                     If None, uses current directory.
        """
        self.game_dir = game_dir if game_dir else "."
        self.logger = logging.getLogger('soliloquy')
        
        # Find directory structure - try multiple locations
        self.scenes_dir = self._find_directory(['scenes'])
        self.items_dir = self._find_directory(['items'])
        self.characters_dir = self._find_directory(['characters'])
        self.achievements_dir = self._find_directory(['achievements'])
        
        # Log found directories
        self.logger.info(f"Found scenes directory: {self.scenes_dir}")
        self.logger.info(f"Found items directory: {self.items_dir}")
        self.logger.info(f"Found characters directory: {self.characters_dir}")
        self.logger.info(f"Found achievements directory: {self.achievements_dir}")
    
    def _find_directory(self, possible_paths: List[str]) -> str:
        """
        Find a directory by trying multiple possible locations.
        
        Args:
            possible_paths: List of possible relative paths
            
        Returns:
            Found directory path or first path if not found
        """
        # First try in game_dir
        for path in possible_paths:
            full_path = os.path.join(self.game_dir, path)
            if os.path.isdir(full_path):
                return full_path
        
        # Then try from current directory
        for path in possible_paths:
            if os.path.isdir(path):
                return path
        
        # Then try parent directory
        parent_dir = os.path.dirname(os.path.abspath('.'))
        for path in possible_paths:
            full_path = os.path.join(parent_dir, path)
            if os.path.isdir(full_path):
                return full_path
        
        # Return default path even if not found (will be logged as warning later)
        return os.path.join(self.game_dir, possible_paths[0])
    
    def load_scenes(self) -> Dict[str, Scene]:
        """
        Load all scene YAML files.
        
        Returns:
            Dict of scene ID to Scene objects
        """
        scenes = {}
        
        if not os.path.isdir(self.scenes_dir):
            self.logger.warning(f"Scenes directory not found at {self.scenes_dir}")
            return scenes
        
        # Find all scene YAML files recursively
        scene_pattern = os.path.join(self.scenes_dir, "**", "*.yaml")
        scene_files = glob.glob(scene_pattern, recursive=True)
        
        self.logger.info(f"Found {len(scene_files)} scene files")
        for scene_file in scene_files:
            try:
                with open(scene_file, 'r') as f:
                    scene_data = yaml.safe_load(f)
                
                # Get scene ID from file path relative to scenes directory
                rel_path = os.path.relpath(scene_file, self.scenes_dir)
                scene_id = os.path.splitext(rel_path)[0].replace(os.path.sep, "/")
                
                # Create scene object
                scene = Scene(scene_id, scene_data)
                scenes[scene_id] = scene
                
                # Also store with simplified ID (without directories)
                simple_id = os.path.splitext(os.path.basename(scene_file))[0]
                if simple_id not in scenes:
                    scenes[simple_id] = scene
                
                self.logger.debug(f"Loaded scene: {scene_id}")
            except Exception as e:
                self.logger.error(f"Error loading scene file {scene_file}: {e}")
                self.logger.debug(traceback.format_exc())
        
        # Print all available scenes for debugging
        self.logger.info(f"Available scenes: {list(scenes.keys())}")
        
        return scenes
    
    def load_items(self) -> Dict[str, Item]:
        """
        Load all item YAML files.
        
        Returns:
            Dict of item ID to Item objects
        """
        items = {}
        
        if not os.path.isdir(self.items_dir):
            self.logger.warning(f"Items directory not found at {self.items_dir}")
            return items
        
        # Find all item YAML files recursively
        item_pattern = os.path.join(self.items_dir, "**", "*.yaml")
        item_files = glob.glob(item_pattern, recursive=True)
        
        self.logger.info(f"Found {len(item_files)} item files")
        for item_file in item_files:
            try:
                with open(item_file, 'r') as f:
                    item_data = yaml.safe_load(f)
                
                # Get item ID from file or from filename if not specified
                item_id = item_data.get("id")
                if not item_id:
                    item_id = os.path.splitext(os.path.basename(item_file))[0]
                
                # Create item object
                item = Item(item_id, item_data)
                items[item_id] = item
                
                self.logger.debug(f"Loaded item: {item_id}")
            except Exception as e:
                self.logger.error(f"Error loading item file {item_file}: {e}")
                self.logger.debug(traceback.format_exc())
        
        return items
    
    def load_characters(self) -> Dict[str, Character]:
        """
        Load all character YAML files.
        
        Returns:
            Dict of character ID to Character objects
        """
        characters = {}
        
        if not os.path.isdir(self.characters_dir):
            self.logger.warning(f"Characters directory not found at {self.characters_dir}")
            return characters
        
        # Find all character YAML files recursively
        char_pattern = os.path.join(self.characters_dir, "**", "*.yaml")
        char_files = glob.glob(char_pattern, recursive=True)
        
        self.logger.info(f"Found {len(char_files)} character files")
        for char_file in char_files:
            try:
                with open(char_file, 'r') as f:
                    char_data = yaml.safe_load(f)
                
                # Get character ID from file or from filename if not specified
                char_id = char_data.get("id")
                if not char_id:
                    char_id = os.path.splitext(os.path.basename(char_file))[0]
                
                # Create character object
                character = Character(char_id, char_data)
                characters[char_id] = character
                
                self.logger.debug(f"Loaded character: {char_id}")
            except Exception as e:
                self.logger.error(f"Error loading character file {char_file}: {e}")
                self.logger.debug(traceback.format_exc())
        
        return characters
    
    def load_achievements(self) -> List[Dict[str, Any]]:
        """
        Load all achievement YAML files.
        
        Returns:
            List of achievement dictionaries
        """
        achievements = []
        
        if not os.path.isdir(self.achievements_dir):
            self.logger.warning(f"Achievements directory not found at {self.achievements_dir}")
            return achievements
        
        # Find all achievement YAML files recursively
        achievement_pattern = os.path.join(self.achievements_dir, "**", "*.yaml")
        achievement_files = glob.glob(achievement_pattern, recursive=True)
        
        self.logger.info(f"Found {len(achievement_files)} achievement files")
        for achievement_file in achievement_files:
            try:
                with open(achievement_file, 'r') as f:
                    achievement_data = yaml.safe_load(f)
                
                achievements.append(achievement_data)
                self.logger.debug(f"Loaded achievement: {achievement_data.get('name', 'Unknown')}")
            except Exception as e:
                self.logger.error(f"Error loading achievement file {achievement_file}: {e}")
                self.logger.debug(traceback.format_exc())
        
        return achievements
