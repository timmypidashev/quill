# soliloquy/command_parser.py
import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, logging as transformers_logging
    # Suppress the transformer warnings
    transformers_logging.set_verbosity_error()
except ImportError:
    # Optional dependencies for neural parsing
    pass

class CommandParser:
    """
    Parser for converting natural language input to game commands.
    Uses a neural model to understand player intent.
    """
    
    def __init__(self, model_name: str = "DeepSeek-AI/deepseek-coder-1.3b-instruct", use_neural: bool = True):
        """
        Initialize the command parser.
        
        Args:
            model_name: Name of the neural model to use
            use_neural: Whether to use neural model (False falls back to rule-based)
        """
        self.logger = logging.getLogger('soliloquy')
        self.use_neural = use_neural
        self.model = None
        self.tokenizer = None
        
        # Try to initialize the neural model if requested
        if use_neural:
            try:
                self.logger.info(f"Initializing neural command parser with model: {model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
                self.logger.info("Neural model loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load neural model: {e}")
                self.logger.info("Falling back to rule-based parsing")
                self.use_neural = False
        
        # Initialize rule-based parser components
        self.verbs = {
            "look": ["look", "examine", "inspect", "check", "view", "see", "observe"],
            "go": ["go", "move", "walk", "run", "travel", "head", "proceed", "enter", "exit", "leave"],
            "take": ["take", "grab", "pick", "collect", "get", "acquire", "steal"],
            "use": ["use", "utilize", "employ", "apply", "operate"],
            "talk": ["talk", "speak", "chat", "converse", "ask", "tell", "say"],
            "inventory": ["inventory", "items", "possessions", "belongings"],
            "drop": ["drop", "discard", "put", "place", "set"]
        }
        
        self.prepositions = ["on", "in", "with", "to", "at", "for", "from", "by", "about"]
    
    def parse(self, user_input: str, current_scene: Any, player: Any) -> Dict[str, Any]:
        """
        Parse user input into a game command.
        
        Args:
            user_input: Natural language input from the player
            current_scene: Current scene object for context
            player: Player object for context
            
        Returns:
            Command dictionary with action and targets
        """
        if self.use_neural and self.model and self.tokenizer:
            try:
                return self._neural_parse(user_input, current_scene, player)
            except Exception as e:
                self.logger.error(f"Neural parsing failed: {e}")
                self.logger.info("Falling back to rule-based parsing")
        
        # Fall back to rule-based parsing
        return self._rule_based_parse(user_input, current_scene, player)

    def _neural_parse(self, user_input: str, current_scene: Any, player: Any) -> Dict[str, Any]:
        """
        Use neural model to parse user input.
        
        Args:
            user_input: Natural language input from the player
            current_scene: Current scene object for context
            player: Player object for context
            
        Returns:
            Command dictionary with action and targets
        """
        # Create prompt with rich context
        visible_objects = current_scene.get_visible_objects(player.get_flags())
        visible_exits = current_scene.get_visible_exits(player.get_flags())
        inventory = player.get_inventory()
        
        # Format visible objects with descriptions for better context
        objects_context = []
        for obj_name, obj_desc in visible_objects.items():
            if isinstance(obj_desc, dict) and "description" in obj_desc:
                objects_context.append(f"{obj_name}: {obj_desc['description']}")
            elif isinstance(obj_desc, str):
                objects_context.append(f"{obj_name}: {obj_desc}")
            else:
                objects_context.append(obj_name)
        
        objects_str = "\n    ".join(objects_context) if objects_context else "None"
        
        # Format exits with targets and descriptions for better context
        exits_context = []
        for exit_name, exit_data in visible_exits.items():
            if isinstance(exit_data, dict):
                target = exit_data.get("target", "unknown")
                desc = exit_data.get("description", "")
                exits_context.append(f"{exit_name} -> {target} ({desc})")
            else:
                exits_context.append(f"{exit_name} -> {exit_data}")
        
        exits_str = "\n    ".join(exits_context) if exits_context else "None"
        
        # Format inventory items
        inventory_str = ", ".join(inventory) if inventory else "Empty"
        
        # Get any characters in the scene
        characters_str = "None"
        if hasattr(current_scene, "characters") and current_scene.characters:
            characters = []
            for char_id, char_data in current_scene.characters.items():
                if isinstance(char_data, dict):
                    char_name = char_data.get("name", char_id)
                    characters.append(char_name)
                else:
                    characters.append(char_id)
            characters_str = ", ".join(characters)
        
        # List of valid exit names for reference
        valid_exits = list(visible_exits.keys())
        valid_exits_str = ", ".join([f'"{exit}"' for exit in valid_exits])
        
        # List of valid object names for reference
        valid_objects = list(visible_objects.keys())
        valid_objects_str = ", ".join([f'"{obj}"' for obj in valid_objects])
        prompt = f"""
<instruction>
You are a command parser for a text adventure game. Your job is to convert natural language input into structured commands, being forgiving of typos and grammatical errors.

Current scene: {current_scene.name}
Description: {current_scene.description[:150]}...

Objects you can interact with:
    {objects_str}

Characters present:
    {characters_str}

Available exits:
    {exits_str}

Inventory:
    {inventory_str}

Commands to output (only these are valid):
- {{"action": "look"}} - Look around the current scene
- {{"action": "examine", "target": "<object_name>"}} - Examine a specific object closely
- {{"action": "go", "target": "<exit_name>"}} - Move to a different scene through an available exit
- {{"action": "take", "target": "<item_name>"}} - Pick up an item
- {{"action": "use", "target": "<item_name>", "indirect_target": "<object_name>"}} - Use an item on an object
- {{"action": "talk", "target": "<character_name>"}} - Talk to a character
- {{"action": "inventory"}} - Check your inventory
- {{"action": "drop", "target": "<item_name>"}} - Drop an item

ESSENTIAL RULES:
1. Be forgiving of typos and grammatical errors. If the user input approximately matches an object, exit, or character name, use the correct name from the available options.

2. For "go" commands, if the exact exit isn't found, use the most similar one:
   - If user says "go to library" but only "library_door" exists, output {{"action": "go", "target": "library_door"}}
   - If user says "lets go to the garden" but only "garden_path" exists, output {{"action": "go", "target": "garden_path"}}

3. For "examine" commands, always match to the closest valid object:
   - If user says "look at chair" but only "armchair" exists, output {{"action": "examine", "target": "armchair"}}
   - If user says "look at bookcase" but only "bookshelves" exists, output {{"action": "examine", "target": "bookshelves"}}

4. For "talk" commands, match to the closest character name:
   - If user says "talk to professor" but character is "professor_blackwood", output {{"action": "talk", "target": "professor_blackwood"}}

5. ALWAYS use action "examine" (not "look") when the user wants to look at a specific object.

6. The "look" action should ONLY be used to look at the entire scene.

Valid exit names: {valid_exits_str}
Valid object names: {valid_objects_str}

Parse this input (be forgiving of errors): "{user_input}"

IMPORTANT: If you are unsure of what to do, please match the most closest command possible. Expect the user to 
make mistakes, say things that might be a bit too long and not perfectly match the available options. Try 
to be as helpful as possible in understanding their intent and converting it into a valid command.

Output ONLY the JSON object representing the command.

Output JUST this: {{"action": "X", "target": "Y"}}
</instruction>
"""
        # Generate response with fixed parameters
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Create attention mask if not provided
        if 'attention_mask' not in inputs:
            inputs['attention_mask'] = torch.ones_like(inputs['input_ids'])
        
        # Generate with corrected parameters
        outputs = self.model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.1,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        
        # Log the raw response for debugging
        self.logger.debug(f"Neural model raw output: '{response}'")
        
        # Clean the response - strip whitespace
        response = response.strip()
        
        # Extract JSON from the response - focus only on this and don't complicate it
        try:
            # If we have a curly brace, try to extract JSON
            if '{' in response and '}' in response:
                # Find start and end of JSON
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                
                # Try to parse it
                command = json.loads(json_str)
                if "action" in command:
                     # Force "look" with target to become "examine"
                    if command["action"] == "look" and "target" in command:
                        self.logger.info(f"Converting 'look' with target to 'examine': {command}")
                        command["action"] = "examine"
                    
                    self.logger.info(f"Successfully parsed command: {command}")
                    return command

        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON: {e}")
        
        # If JSON parsing failed, fall back to rule-based
        self.logger.warning("Falling back to rule-based parsing")
        return self._rule_based_parse(user_input, current_scene, player)

    def _rule_based_parse(self, user_input: str, current_scene: Any, player: Any) -> Dict[str, Any]:
        """
        Use rule-based approach to parse user input.
        
        Args:
            user_input: Natural language input from the player
            current_scene: Current scene object for context
            player: Player object for context
            
        Returns:
            Command dictionary with action and targets
        """
        # Normalize input
        normalized_input = user_input.lower()
        words = normalized_input.split()
        
        # Empty input
        if not words:
            return {"action": "invalid"}
        
        # Special case handling for common phrasings
        if "go up" in normalized_input or "climb" in normalized_input:
            if "staircase" in normalized_input or "stairs" in normalized_input:
                return {"action": "go", "target": "staircase"}
        
        if "go to" in normalized_input or "head to" in normalized_input or "lets go" in normalized_input:
            exits = current_scene.get_visible_exits(player.get_flags())
            for exit_name in exits:
                if exit_name.lower() in normalized_input:
                    return {"action": "go", "target": exit_name}
        
        # Handle "look around" and similar
        if any(phrase in normalized_input for phrase in ["look around", "search", "check around", "look for clues"]):
            return {"action": "look"}
        
        # Handle "look at X" or "examine X"
        look_at_match = re.search(r"look at(?: the)? (.+)", normalized_input)
        if look_at_match:
            target = look_at_match.group(1).strip()
            return {"action": "examine", "target": target}
        
        # Handle "check inventory", "show inventory", etc.
        if any(phrase in normalized_input for phrase in ["inventory", "my items", "what do i have"]):
            return {"action": "inventory"}
        
        # Original logic continues below
        
        # Single-word commands
        if len(words) == 1:
            word = words[0]
            
            # Check for inventory command
            if word in self.verbs["inventory"]:
                return {"action": "inventory"}
                
            # Check for look command
            if word in self.verbs["look"]:
                return {"action": "look"}
                
            # Check if it's a direction/exit
            exits = current_scene.get_visible_exits(player.get_flags())
            if word in exits:
                return {"action": "go", "target": word}
        
        # Multi-word commands
        action, target, indirect = self._extract_command_parts(words)
        
        # Handle special cases
        if action in self.verbs["inventory"]:
            return {"action": "inventory"}
            
        if action in self.verbs["look"] and not target:
            return {"action": "look"}
        
        # Map verb synonyms to canonical actions
        canonical_action = None
        for key, synonyms in self.verbs.items():
            if action in synonyms:
                canonical_action = key
                break
        
        if not canonical_action:
            # Try to recover by checking for exits in the input
            exits = current_scene.get_visible_exits(player.get_flags())
            for exit_name in exits:
                if exit_name.lower() in normalized_input:
                    return {"action": "go", "target": exit_name}
            
            return {"action": "invalid", "original_input": user_input}
            
        # Build command
        command = {"action": canonical_action}
        
        if target:
            command["target"] = target
            
        if indirect:
            command["indirect_target"] = indirect
            
        return command 

    def _extract_command_parts(self, words: List[str]) -> Tuple[str, str, str]:
        """
        Extract action, target, and indirect target from words.
        
        Args:
            words: List of words from user input
            
        Returns:
            Tuple of (action, target, indirect_target)
        """
        action = words[0]
        target = ""
        indirect_target = ""
        
        # Find prepositions to split the command
        preposition_indices = [i for i, word in enumerate(words) if word in self.prepositions]
        
        if not preposition_indices:
            # No prepositions, everything after verb is the target
            if len(words) > 1:
                target = " ".join(words[1:])
        else:
            # First part is the target
            first_prep_index = preposition_indices[0]
            if first_prep_index > 1:
                target = " ".join(words[1:first_prep_index])
                
            # Part after preposition is indirect target
            if first_prep_index < len(words) - 1:
                indirect_target = " ".join(words[first_prep_index+1:])
        
        return action, target, indirect_target
