#!/usr/bin/env python3
"""
Screenshot Organizer - Main Entry Point
Choose between command line or TUI interface.
"""

import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Screenshot Organizer - Organize screenshot files by date",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Launch TUI interface
  python main.py --cli                    # Use command line interface
  python main.py --cli --preview          # Preview mode (CLI)
  python main.py --cli --source ~/Desktop --target ~/Desktop/Screenshots
        """
    )
    
    parser.add_argument("--cli", action="store_true", 
                       help="Use command line interface instead of TUI")
    parser.add_argument("--source", "-s", type=Path,
                       help="Source directory (CLI mode only)")
    parser.add_argument("--target", "-t", type=Path,
                       help="Target directory (CLI mode only)")
    parser.add_argument("--preview", "-p", action="store_true",
                       help="Preview mode - don't actually move files (CLI mode only)")
    parser.add_argument("--copy", "-c", action="store_true",
                       help="Copy files instead of moving them (CLI mode only)")
    parser.add_argument("--pattern", type=str,
                       help="Custom regex pattern for matching files (CLI mode only)")
    parser.add_argument("--recursive", "-r", action="store_true",
                       help="Search subdirectories recursively (CLI mode only)")
    
    args = parser.parse_args()
    
    if args.cli:
        # Use command line interface
        from screenshot_organizer import main as cli_main
        # Override sys.argv to pass arguments to the CLI
        cli_args = ["screenshot_organizer.py"]
        if args.source:
            cli_args.extend(["--source", str(args.source)])
        if args.target:
            cli_args.extend(["--target", str(args.target)])
        if args.preview:
            cli_args.append("--preview")
        if args.copy:
            cli_args.append("--copy")
        if args.pattern:
            cli_args.extend(["--pattern", args.pattern])
        if args.recursive:
            cli_args.append("--recursive")
            
        sys.argv = cli_args
        cli_main()
    else:
        # Use TUI interface
        try:
            from screenshot_tui import main as tui_main
            tui_main()
        except ImportError as e:
            print(f"Error: Could not import TUI dependencies: {e}")
            print("Try installing dependencies with: pip install textual")
            sys.exit(1)


if __name__ == "__main__":
    main()
