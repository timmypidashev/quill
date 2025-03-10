import os
import sys
import argparse
from .engine import QuillEngine

def main():
    """Main entry point for the Quill CLI."""
    parser = argparse.ArgumentParser(description="Quill Text Adventure Engine")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Run game command
    run_parser = subparsers.add_parser("run", help="Run a Quill game")
    run_parser.add_argument("game_dir", help="Directory containing game YAML files")
    run_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--parser", choices=["basic", "api", "local"], default="basic",
                       help="Type of command parser to use (basic=rule-based, api=OpenAI, local=neural model)")
    parser.add_argument("--model", default="DeepSeek-AI/deepseek-coder-1.3b-instruct",
                       help="Model name for local neural parsing")
    
    # Create game command
    create_parser = subparsers.add_parser("create", help="Create a new Quill game")
    create_parser.add_argument("game_name", help="Name of the new game")
    create_parser.add_argument("--destination", "-d", default=".", help="Destination directory")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return 1
    
    # Run a game
    if args.command == "run":
        if not os.path.isdir(args.game_dir):
            print(f"Error: Game directory '{args.game_dir}' not found.")
            return 1
        
        engine = QuillEngine(
            args.game_dir,
            parser_type=args.parser,
            model_name=args.model,
            debug=args.debug
        )
        engine.start_game()
    
    # Create a new game
    elif args.command == "create":
        from soliloquy.utils.game_creator import create_new_game
        create_new_game(args.game_name, args.destination)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

