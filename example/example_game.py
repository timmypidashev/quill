#!/usr/bin/env python3
# example_game.py
import os
import sys
import argparse
from soliloquy.engine import SoliloquyEngine

def main():
    """Main entry point for the example game."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a Soliloquy text adventure game")
    parser.add_argument("--game-dir", help="Optional directory containing game YAML files", default=None)
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--parser", choices=["local", "api", "basic"], default="basic",
                       help="Type of command parser to use (local=neural model, api=OpenAI, basic=rule-based)")
    parser.add_argument("--model", default="DeepSeek-AI/deepseek-coder-1.3b-instruct",
                       help="Model name for local neural parsing")
    args = parser.parse_args()
    
    # Set up OpenAI API key from environment if using API parser
    if args.parser == "api" and not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: Using 'api' parser but OPENAI_API_KEY environment variable is not set.")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        print("Falling back to 'basic' parser.")
        args.parser = "basic"
    
    # Initialize and start the game engine
    engine = SoliloquyEngine(args.game_dir, parser_type=args.parser, model_name=args.model)
    engine.start_game()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
