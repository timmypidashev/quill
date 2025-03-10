import os
import sys
import argparse
from .engine import QuillEngine

def main():
    """Main entry point for a quill game."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a quill text adventure game")
    parser.add_argument("--game-dir", help="Optional directory containing game YAML files", default=None)
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--parser", choices=["basic", "api", "local"], default="basic",
                       help="Type of command parser to use (basic=rule-based, api=OpenAI, local=neural model)")
    parser.add_argument("--model", default="DeepSeek-AI/deepseek-coder-1.3b-instruct",
                       help="Model name for local neural parsing")
    parser.add_argument("--save-dir", help="Directory for save files", default=None)
    parser.add_argument("--load", type=int, help="Load a specific save ID on startup", default=None)
    args = parser.parse_args()
    
    # Set up OpenAI API key from environment if using API parser
    if args.parser == "api" and not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: Using 'api' parser but OPENAI_API_KEY environment variable is not set.")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        print("Falling back to 'basic' parser.")
        args.parser = "basic"
    
    # Initialize the game engine
    engine = QuillEngine(
        args.game_dir, 
        parser_type=args.parser, 
        model_name=args.model,
        save_dir=args.save_dir,
        debug=args.debug
    )
    
    # Load game
    if not engine.load_game():
        print("Failed to load game.")
        return 1
    
    # Load a specific save if requested
    if args.load is not None:
        if not engine.load_game(args.load):
            print(f"Failed to load save ID {args.load}")
            print("Starting new game instead.")
    
    # Start the game
    engine.start_game()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
