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
    parser.add_argument("--debug", action="store_true", default=False, help="Enable debug mode")
    args = parser.parse_args()
    
    # Initialize and start the game engine
    engine = SoliloquyEngine()
    engine.start_game()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
