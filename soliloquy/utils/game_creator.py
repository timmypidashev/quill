import os
import shutil
import yaml
from pathlib import Path

def create_new_game(game_name, destination="."):
    """
    Create a new Soliloquy game with basic structure.
    
    Args:
        game_name: Name of the game
        destination: Destination directory
    """
    # Create game directory
    game_dir = os.path.join(destination, game_name.lower().replace(" ", "_"))
    
    if os.path.exists(game_dir):
        print(f"Error: Directory '{game_dir}' already exists.")
        return False
    
    # Create directory structure
    dirs = [
        "",
        "scenes",
        "items",
        "characters",
        "achievements"
    ]
    
    for d in dirs:
        os.makedirs(os.path.join(game_dir, d), exist_ok=True)
    
    # Create game.yaml
    game_config = {
        "title": game_name,
        "author": "Your Name",
        "version": "0.1.0",
        "description": f"A new text adventure created with Soliloquy.",
        "tags": ["adventure", "example"],
        "banner": f"{game_name.upper()}",
        "starting_scene": "starting_room"
    }
    
    with open(os.path.join(game_dir, "game.yaml"), "w") as f:
        yaml.dump(game_config, f, default_flow_style=False)
    
    # Create a basic starting room
    starting_room = {
        "name": "Starting Room",
        "description": "You stand in an empty room. This is the beginning of your adventure.",
        "exits": {},
        "objects": {
            "walls": {
                "description": "Blank walls surround you. The possibilities are endless!"
            }
        }
    }
    
    with open(os.path.join(game_dir, "scenes", "starting_room.yaml"), "w") as f:
        yaml.dump(starting_room, f, default_flow_style=False)
    
    print(f"Created new game '{game_name}' in {game_dir}")
    print("To run your game, use: soliloquy run", game_dir)
    
    return True
