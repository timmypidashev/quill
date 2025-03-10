import os
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformers import logging as transformers_logging
    # Suppress transformer warnings
    transformers_logging.set_verbosity_error()
except ImportError:
    # Optional dependencies for neural parsing
    pass

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

class CommandParser:
    """
    Parser for converting natural language input to game commands.
    """
    
    def __init__(self, parser_type: str = "local", model_name: str = "DeepSeek-AI/deepseek-coder-1.3b-instruct"):
        """
        Initialize the command parser.
        
        Args:
            parser_type: Type of parser to use ("local", "api", or "basic")
            model_name: Name of the neural model to use (for local parser)
        """
        self.logger = logging.getLogger('soliloquy')
        self.parser_type = parser_type.lower()
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        # Initialize parser based on type
        if self.parser_type == "local":
            self._init_local_model()
        elif self.parser_type == "api":
            self._init_api()
        
        # Initialize rule-based parser components (used by all parser types)
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
    
    def _init_local_model(self):
        """Initialize the local neural model."""
        try:
            self.logger.info(f"Initializing local neural model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model in half precision
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            
            self.logger.info("Local neural model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load local neural model: {e}")
            self.parser_type = "basic"
    
    def _init_api(self):
        """Initialize the API-based parser."""
        if not HAS_OPENAI:
            self.logger.error("OpenAI package not installed. Run 'pip install openai'")
            self.parser_type = "basic"
            return
            
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self.logger.error("No OpenAI API key found in OPENAI_API_KEY environment variable")
            self.parser_type = "basic"
            return
            
        try:
            openai.api_key = api_key
            self.logger.info("OpenAI API initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI API: {e}")
            self.parser_type = "basic"
    
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
        if self.parser_type == "local" and self.model and self.tokenizer:
            try:
                return self._neural_parse(user_input, current_scene, player)
            except Exception as e:
                self.logger.error(f"Neural parsing failed: {e}")
                self.logger.info("Falling back to rule-based parsing")
        
        elif self.parser_type == "api":
            try:
                return self._api_parse(user_input, current_scene, player)
            except Exception as e:
                self.logger.error(f"API parsing failed: {e}")
                self.logger.info("Falling back to rule-based parsing")
        
        # Fall back to rule-based parsing
        return self._rule_based_parse(user_input, current_scene, player)
    
    def _create_prompt(self, user_input: str, current_scene: Any, player: Any) -> str:
        """
        Create the prompt to send to models.
        
        Args:
            user_input: Natural language input from the player
            current_scene: Current scene object for context
            player: Player object for context
            
        Returns:
            Prompt string
        """
        # Create prompt with rich context
        visible_objects = current_scene.get_visible_objects(player.get_flags())
        visible_exits = current_scene.get_visible_exits(player.get_flags())
        inventory = player.get_inventory()
        
        # Format objects with descriptions for better context
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
You are a command parser for a text adventure game. You MUST output ONLY a single valid JSON object and nothing else.

Current scene: {current_scene.name}
Description: {current_scene.description[:150]}...

Objects in the scene:
    {objects_str}

Characters in the scene:
    {characters_str}

Available exits:
    {exits_str}

Inventory:
    {inventory_str}

Valid commands are:
- {{"action": "look"}} - Look around the current scene
- {{"action": "examine", "target": "<object_name>"}} - Examine a specific object closely
- {{"action": "go", "target": "<exit_name>"}} - Move to a different scene through an available exit
- {{"action": "take", "target": "<item_name>"}} - Pick up an item
- {{"action": "use", "target": "<item_name>", "indirect_target": "<object_name>"}} - Use an item on an object
- {{"action": "talk", "target": "<character_name>"}} - Talk to a character
- {{"action": "inventory"}} - Check your inventory
- {{"action": "drop", "target": "<item_name>"}} - Drop an item

CRITICAL RULES:
1. For "go" commands, you MUST use the EXACT exit name from this list: {valid_exits_str}
   For example, if the user says "go to library" but the exit is named "library_door", use "library_door".
2. For "examine" commands, you MUST use the EXACT object name from this list: {valid_objects_str}
3. For "examine" commands, ALWAYS use the action "examine" when the user wants to look at a specific object.
4. Output ONLY a raw JSON object with no additional text.
5. "look" alone is for looking at the entire scene, not specific objects.
6. STRICTLY use ONLY the exact names listed above for exits and objects.

Parse this input: "{user_input}"

Output ONLY the JSON object representing the command.
"""
        return prompt
    
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
        prompt = self._create_prompt(user_input, current_scene, player)
        
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
                    self.logger.info(f"Successfully parsed command: {command}")
                    return command
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON: {e}")
        
        # If JSON parsing failed, fall back to rule-based
        self.logger.warning("Falling back to rule-based parsing")
        return self._rule_based_parse(user_input, current_scene, player)
    
    def _api_parse(self, user_input: str, current_scene: Any, player: Any) -> Dict[str, Any]:
        """
        Use OpenAI API to parse user input.
        
        Args:
            user_input: Natural language input from the player
            current_scene: Current scene object for context
            player: Player object for context
            
        Returns:
            Command dictionary with action and targets
        """
        prompt = self._create_prompt(user_input, current_scene, player)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a command parser that only outputs valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            if response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content.strip()
                self.logger.debug(f"OpenAI API response: {response_text}")
                
                # Extract and parse JSON
                try:
                    # Try to find JSON in the response
                    json_match = re.search(r'({.*})', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        command = json.loads(json_str)
                        if "action" in command:
                            self.logger.info(f"Successfully parsed command: {command}")
                            return command
                except Exception as e:
                    self.logger.warning(f"Failed to parse JSON from API response: {e}")
            
            self.logger.warning(f"Invalid response from OpenAI API")
            return self._rule_based_parse(user_input, current_scene, player)
            
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
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
        # [Your existing rule-based parsing code]
        # Normalize input
        words = user_input.lower().split()
        
        # Empty input
        if not words:
            return {"action": "invalid"}
            
        # Handle "look around" specially
        if user_input.lower() in ["look around", "look around for clues"]:
            return {"action": "look"}
        
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
            return {"action": "invalid", "original_input": user_input}
            
        # Build command
        command = {"action": canonical_action}
        
        if target:
            command["target"] = target
            
        if indirect:
            command["indirect_target"] = indirect
        
        # Force "look" with target to become "examine"
        if command["action"] == "look" and "target" in command:
            self.logger.info(f"Converting 'look' with target to 'examine': {command}")
            command["action"] = "examine"
            
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
