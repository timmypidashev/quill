# soliloquy
A modern text-based adventure engine that transforms natural writing into interactive experiences.

## Features

- Simple YAML-based game definition
- Modern terminal UI with text effects and colors
- Natural language command processing
- Character dialogue system
- Inventory management
- Game state tracking with flags
- Hidden objects and secret passages
- Events and conditional triggers

## Installation

```bash
pip install soliloquy
```

For neural language processing features (optional):
```bash
pip install soliloquy[neural]
```

## Quick Start

Create a new game:
```bash
soliloquy create "My Adventure"
```

Run your game:
```bash
soliloquy run my_adventure
```

## Game Structure

A Soliloquy game consists of YAML files organized in the following structure:

```
game.yaml                # Main game configuration
scenes/                  # Scene definitions
  starting_room.yaml
  ...
items/                   # Item definitions
  key.yaml
  ...
characters/              # Character definitions
  npc.yaml
  ...
achievements/            # Achievement definitions
  explorer.yaml
  ...
```

See the documentation for detailed information on creating your own adventures.

## Example

Here's a simple example of a scene definition:

```yaml
name: "Forest Clearing"
description: "A peaceful clearing in the forest. Sunlight filters through the canopy, illuminating a stone pedestal in the center."

exits:
  north:
    target: "deep_forest"
    description: "A narrow path leads deeper into the forest."
  
  south:
    target: "forest_entrance"
    description: "The path back to the forest entrance."

objects:
  pedestal:
    description: "A weathered stone pedestal with a small indentation on top, perfectly sized for a gem."
  
  flowers:
    description: "Colorful wildflowers dot the clearing."

events:
  place_gem:
    trigger: "place gem on pedestal"
    condition:
      has_flags: ["has_gem"]
    message: "You place the gem on the pedestal. It begins to glow, and a hidden door opens in a nearby tree trunk!"
    flags_set: ["door_revealed"]
```
