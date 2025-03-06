# soliloquy/engine.py
import os
import glob
import time
import yaml
from typing import Dict, List, Optional, Any

from .game_loader import GameLoader
from .player import Player
from .scene import Scene
from .character import Character
from .item import Item
from .command_parser import CommandParser
from .ui.console import Console
from .ui.text_effects import TypeWriter
from .ui.dialogue_ui import DialogueMenu
from .ui.inventory_ui import InventoryDisplay
from .utils.spinner import Spinner
from .utils.ascii_art import display_ascii_art
from .utils.logger import setup_logger

class SoliloquyEngine:
    """
    Main game engine for Soliloquy text adventure games.
    """
    
    def __init__(self, game_dir: str = None):
        """
        Initialize the Soliloquy game engine.
        
        Args:
            game_dir: Directory containing game YAML files
        """
        self.logger = setup_logger('soliloquy')
        self.logger.info("Initializing Soliloquy Engine")
        
        self.game_dir = game_dir if game_dir else "."
        self.console = Console()
        self.spinner = Spinner()
        self.typewriter = TypeWriter()
        self.dialogue_menu = DialogueMenu()
        self.inventory_display = InventoryDisplay()
        
        # Game state
        self.game_data = {}
        self.scenes = {}
        self.items = {}
        self.characters = {}
        self.player = Player()
        self.current_scene = None
        self.game_running = False
        
        # Initialize command parser with neural model
        self.command_parser = CommandParser()
        
    def load_game(self) -> bool:
        """
        Load game data from YAML files.
        
        Returns:
            bool: True if game loaded successfully
        """
        try:
            # Load main game file
            game_file = os.path.join(self.game_dir, "game.yaml")
            if not os.path.exists(game_file):
                self.logger.error(f"Game file not found: {game_file}")
                return False
                
            with open(game_file, 'r') as f:
                self.game_data = yaml.safe_load(f)
            
            # Display game banner
            if "banner" in self.game_data:
                display_ascii_art(self.game_data["banner"])
            
            self.console.print_title(self.game_data["title"])
            self.console.print_info(f"By {self.game_data['author']}")
            self.console.print_description(self.game_data["description"])
            
            # Load all scenes
            loader = GameLoader(self.game_dir)
            self.scenes = loader.load_scenes()
            self.items = loader.load_items()
            self.characters = loader.load_characters()
            
            # Set starting scene
            starting_scene = self.game_data.get("starting_scene")
            if starting_scene not in self.scenes:
                self.logger.error(f"Starting scene not found: {starting_scene}")
                return False
                
            self.current_scene = self.scenes[starting_scene]
            return True
            
        except Exception as e:
            self.logger.exception(f"Error loading game: {e}")
            return False
    
    def start_game(self):
        """Start the game loop."""
        if not self.load_game():
            self.console.print_error("Failed to load game.")
            return
        
        self.game_running = True
        self.display_current_scene()
        
        while self.game_running:
            # Get player input
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["quit", "exit", "q"]:
                self.game_running = False
                self.console.print_info("Thanks for playing!")
                break
            
            # Show spinner while processing
            self.spinner.start("Thinking")
            
            try:
                # Process input through neural model
                command = self.command_parser.parse(user_input, self.current_scene, self.player)
                
                # Stop spinner before processing command (so text isn't cleared)
                self.spinner.stop()
                
                # Process command
                self.process_command(command)
            except Exception as e:
                self.spinner.stop()
                self.logger.exception(f"Error processing command: {e}")
                self.console.print_error("Sorry, something went wrong processing that command.")

    def display_current_scene(self):
        """Display the current scene description and available exits."""
        if not self.current_scene:
            return
            
        # Check for state-specific descriptions
        description = self.current_scene.get_description(self.player.flags)
        
        # Display scene name and description
        self.console.print_scene_title(self.current_scene.name)
        self.typewriter.print(description)
        
        # Display visible exits
        visible_exits = self.current_scene.get_visible_exits(self.player.flags)
        if visible_exits:
            self.console.print_exits(visible_exits)
        
        # Display visible objects
        visible_objects = self.current_scene.get_visible_objects(self.player.flags)
        if visible_objects:
            self.console.print_objects(visible_objects)
        
        # Display characters in the scene
        characters_in_scene = self.get_characters_in_scene()
        if characters_in_scene:
            self.console.print_characters(characters_in_scene)
    
    def process_command(self, command: Dict[str, Any]):
        """
        Process the parsed command.
        
        Args:
            command: Parsed command dictionary with action and targets
        """
        action = command.get("action")
        if not action:
            self.console.print_error("I don't understand what you want to do.")
            return
            
        # Check for events that might trigger from this command
        self.check_events(action, command.get("target", ""), command.get("indirect_target", ""))
        
        # Basic commands
        if action == "look":
            self.display_current_scene()
        
        elif action == "go":
            target = command.get("target", "")
            self.handle_movement(target)
        
        elif action == "examine":
            target = command.get("target", "")
            self.examine_object(target)
        
        elif action == "take":
            target = command.get("target", "")
            self.take_item(target)
        
        elif action == "use":
            target = command.get("target", "")
            indirect = command.get("indirect_target", "")
            self.use_item(target, indirect)
        
        elif action == "inventory" or action == "inv":
            self.display_inventory()
        
        elif action == "talk":
            target = command.get("target", "")
            self.talk_to_character(target)
        
        else:
            self.console.print_error(f"I don't know how to '{action}'.")
    
    def handle_movement(self, exit_name: str):
        """Handle player movement between scenes."""
        exits = self.current_scene.get_visible_exits(self.player.flags)
        
        # Try to find the exit by name
        found_exit = None
        for exit_key, exit_data in exits.items():
            if exit_key.lower() == exit_name.lower():
                found_exit = exit_data
                break
        
        if not found_exit:
            self.console.print_error(f"There's no '{exit_name}' that you can see.")
            return
        
        # Check if exit is locked
        if self.current_scene.is_exit_locked(exit_key, self.player.flags):
            locked_message = self.current_scene.get_locked_exit_message(exit_key)
            self.typewriter.print(locked_message)
            return
        
        # Move to the new scene
        target_scene = found_exit.get("target")
        if target_scene in self.scenes:
            self.current_scene = self.scenes[target_scene]
            self.display_current_scene()
        else:
            self.console.print_error(f"Error: Scene '{target_scene}' not found.")
    
    def examine_object(self, object_name: str):
        """Examine an object in the current scene."""
        # Check if it's an object in the scene
        if self.current_scene.has_object(object_name):
            description = self.current_scene.get_object_description(object_name, self.player.flags)
            self.typewriter.print(description)
            
            # Check if examining reveals hidden objects
            self.current_scene.reveal_hidden_objects(object_name, self.player)
            return
        
        # Check if it's an item in inventory
        if self.player.has_item(object_name):
            item = self.items.get(object_name)
            if item and "examination" in item:
                self.typewriter.print(item["examination"]["text"])
                return
        
        self.console.print_error(f"You don't see any '{object_name}' here.")
    
    def take_item(self, item_name: str):
        """Take an item from the current scene."""
        item_id = self.current_scene.find_item(item_name)
        
        if not item_id:
            self.console.print_error(f"There's no '{item_name}' here that you can take.")
            return
        
        # Check if item is takeable
        item = self.items.get(item_id)
        if not item or not item.get("takeable", True):
            self.typewriter.print(f"You can't take the {item_name}.")
            return
        
        # Check if item is locked
        if self.current_scene.is_item_locked(item_id, self.player.flags):
            locked_message = self.current_scene.get_locked_item_message(item_id)
            self.typewriter.print(locked_message)
            return
        
        # Take the item
        self.player.add_item(item_id)
        self.current_scene.remove_item(item_id)
        self.typewriter.print(f"You take the {item.get('name', item_name)}.")
    
    def use_item(self, item_name: str, target_name: str = ""):
        """Use an item, possibly on a target."""
        if not self.player.has_item(item_name):
            self.console.print_error(f"You don't have a '{item_name}' to use.")
            return
        
        item = self.items.get(item_name)
        if not item:
            self.console.print_error(f"Item '{item_name}' not found in game data.")
            return
        
        # Using item on something
        if target_name:
            effect_key = f"use_on_{target_name}"
            if "effects" in item and effect_key in item["effects"]:
                effect = item["effects"][effect_key]
                self.typewriter.print(effect.get("message", f"You use the {item_name} on the {target_name}."))
                
                # Set any flags from the effect
                if "flags_set" in effect:
                    for flag in effect["flags_set"]:
                        self.player.add_flag(flag)
                
                return
            
            # Check for scene-specific events for this item use
            event_trigger = f"use {item_name} on {target_name}"
            if self.check_events(event_trigger):
                return
            
            self.console.print_error(f"You can't use the {item_name} on the {target_name} like that.")
        else:
            # Using item by itself
            if "effects" in item and "use" in item["effects"]:
                effect = item["effects"]["use"]
                self.typewriter.print(effect.get("message", f"You use the {item_name}."))
                
                # Set any flags from the effect
                if "flags_set" in effect:
                    for flag in effect["flags_set"]:
                        self.player.add_flag(flag)
                
                return
            
            # Check for scene-specific events for this item use
            event_trigger = f"use {item_name}"
            if self.check_events(event_trigger):
                return
            
            self.console.print_error(f"You're not sure how to use the {item_name} here.")
    
    def talk_to_character(self, character_name: str):
        """Talk to a character in the current scene."""
        characters = self.get_characters_in_scene()
        
        # Find the character by name
        character = None
        for char_id, char_data in characters.items():
            if char_data.get("name", "").lower() == character_name.lower() or char_id.lower() == character_name.lower():
                character = char_data
                break
        
        if not character:
            self.console.print_error(f"There's no '{character_name}' here to talk to.")
            return
        
        # Get dialogue based on state
        dialogue = character.get_dialogue(self.player.flags)
        
        # Display dialogue menu
        self.dialogue_menu.show_dialogue(character.get("name", ""), dialogue["text"], dialogue["options"])
        
        # Get player choice
        choice = self.dialogue_menu.get_choice()
        if choice is None:
            return
        
        # Display response
        option = dialogue["options"][choice]
        self.typewriter.print(f"{character.get('name', '')}: {option['response']}")
        
        # Process any actions from dialogue
        if "actions" in option:
            for action in option["actions"]:
                if action["type"] == "set_flag":
                    self.player.add_flag(action["flag"])
                elif action["type"] == "give_item":
                    self.player.add_item(action["item"])
                    item_name = self.items.get(action["item"], {}).get("name", action["item"])
                    self.typewriter.print(f"* {character.get('name', '')} gives you the {item_name}.")
    
    def display_inventory(self):
        """Display player inventory."""
        inventory = self.player.get_inventory()
        if not inventory:
            self.typewriter.print("Your inventory is empty.")
            return
        
        item_names = []
        for item_id in inventory:
            item = self.items.get(item_id, {})
            item_names.append(item.get("name", item_id))
        
        self.inventory_display.show(item_names)
    
    def check_events(self, action: str, target: str = "", indirect_target: str = "") -> bool:
        """
        Check for and trigger any events in the current scene.
        
        Returns:
            bool: True if an event was triggered
        """
        # Construct possible event triggers
        triggers = [
            action,
            f"{action} {target}",
            f"{action} {target} on {indirect_target}"
        ]
        
        # Check if any triggers match scene events
        for trigger in triggers:
            triggered_event = self.current_scene.check_event(trigger.strip(), self.player.flags)
            if triggered_event:
                # Display event message
                self.typewriter.print(triggered_event.get("message", ""))
                
                # Set any flags
                if "flags_set" in triggered_event:
                    for flag in triggered_event["flags_set"]:
                        self.player.add_flag(flag)
                
                # Add any items
                if "items_add" in triggered_event:
                    for item in triggered_event["items_add"]:
                        self.player.add_item(item)
                        item_name = self.items.get(item, {}).get("name", item)
                        self.typewriter.print(f"* You got: {item_name}")
                
                # Check for scene change
                if "change_scene" in triggered_event:
                    target_scene = triggered_event["change_scene"]
                    if target_scene in self.scenes:
                        self.current_scene = self.scenes[target_scene]
                        self.display_current_scene()
                
                return True
        
        return False
    
    def get_characters_in_scene(self) -> Dict[str, Character]:
        """Get characters present in the current scene."""
        characters_in_scene = {}
        for char_id, char_data in self.characters.items():
            # Check if character should be in this scene
            if self.current_scene.has_character(char_id, self.player.flags):
                characters_in_scene[char_id] = char_data
        
        return characters_in_scene
