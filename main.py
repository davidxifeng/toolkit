#!/usr/bin/env python3
"""
Toolkit - A collection of useful system utilities and tools.

Main entry point that provides a menu-driven interface to select and run tools.
"""

import argparse
import sys
from pathlib import Path


def list_available_tools():
    """List all available tools in the toolkit."""
    tools = {
        "screenshot": {
            "name": "Screenshot Organizer",
            "description": "Organize screenshot files by date with CLI or TUI interface",
            "module": "tools.screenshot"
        },
        "image": {
            "name": "Image Reorganizer", 
            "description": "Convert horizontally concatenated images to 2D grid layout",
            "module": "tools.image.reorganizer"
        }
    }
    return tools


def show_menu():
    """Display the main tool selection menu."""
    tools = list_available_tools()
    
    print("\n🧰 Toolkit - Select a tool to run:")
    print("=" * 40)
    
    for i, (key, tool) in enumerate(tools.items(), 1):
        print(f"{i}. {tool['name']}")
        print(f"   {tool['description']}")
        print()
    
    print("0. Exit")
    print("=" * 40)
    
    while True:
        try:
            choice = input("Enter your choice (0-{}): ".format(len(tools)))
            choice_num = int(choice)
            
            if choice_num == 0:
                print("Goodbye! 👋")
                return None
            elif 1 <= choice_num <= len(tools):
                tool_key = list(tools.keys())[choice_num - 1]
                return tool_key
            else:
                print(f"Please enter a number between 0 and {len(tools)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            return None


def run_screenshot_tool(args):
    """Run the screenshot organizer tool."""
    if args and len(args) > 0 and args[0] == "--tui":
        # Run TUI interface
        try:
            from tools.screenshot.tui import main as tui_main
            sys.argv = ["screenshot_tui"] + args[1:]
            tui_main()
        except ImportError as e:
            print(f"Error: Could not import TUI dependencies: {e}")
            print("Try installing dependencies with: pip install textual")
            sys.exit(1)
    else:
        # Run CLI interface
        from tools.screenshot.organizer import main as cli_main
        sys.argv = ["screenshot_organizer"] + (args or [])
        cli_main()


def run_image_tool(args):
    """Run the image reorganizer tool."""
    from tools.image.reorganizer import main as image_main
    sys.argv = ["image_reorganizer"] + (args or [])
    image_main()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Toolkit - A collection of useful system utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available tools:
  screenshot    Screenshot organizer (CLI and TUI modes)
  image         Image reorganizer (horizontal strip to 2D grid)

Examples:
  python main.py                                    # Interactive menu
  python main.py screenshot --help                  # Screenshot tool help
  python main.py screenshot --tui                   # Screenshot TUI mode
  python main.py image input.png --scale 0.5        # Image reorganizer
        """
    )
    
    parser.add_argument("tool", nargs="?", 
                       help="Tool to run (screenshot, image)")
    parser.add_argument("args", nargs="*", 
                       help="Arguments to pass to the selected tool")
    
    # Parse known args to allow tool-specific arguments
    parsed_args, remaining_args = parser.parse_known_args()
    
    # Combine remaining args with parsed args
    all_tool_args = (parsed_args.args or []) + remaining_args
    
    if not parsed_args.tool:
        # Interactive mode - show menu
        selected_tool = show_menu()
        if selected_tool is None:
            return
        
        # Get additional arguments for the selected tool
        print(f"\nRunning {list_available_tools()[selected_tool]['name']}...")
        print("Use Ctrl+C to return to the main menu\n")
        
        if selected_tool == "screenshot":
            run_screenshot_tool([])
        elif selected_tool == "image":
            print("Image tool requires arguments. Use: python main.py image --help")
            return
    else:
        # Direct tool invocation
        if parsed_args.tool == "screenshot":
            run_screenshot_tool(all_tool_args)
        elif parsed_args.tool == "image":
            run_image_tool(all_tool_args)
        else:
            print(f"Error: Unknown tool '{parsed_args.tool}'")
            print("Available tools: screenshot, image")
            sys.exit(1)


if __name__ == "__main__":
    main()