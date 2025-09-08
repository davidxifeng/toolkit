# Screenshot Organizer

A simple tool to automatically organize screenshot files by date into a clean folder structure.

## Features

- **Smart Organization**: Automatically sorts screenshots into `YYYY-MM-MonthName/WeekNN/` folders
- **Beautiful TUI**: Interactive terminal interface built with Textual
- **Fast CLI**: Command-line interface for automation and scripting
- **Pattern Matching**: Recognizes macOS screenshot format: `Screenshot YYYY-MM-DD at HH.MM.SS.png`
- **Flexible Options**: Move or copy files, preview before processing
- **Smart Filtering**: Only processes valid image files (.png, .jpg, .jpeg, etc.)

## Installation

```bash
# Install dependencies
uv sync

# Or with pip
pip install textual
```

## Usage

### TUI Interface (Default)

Launch the interactive terminal interface:

```bash
python main.py
```

Features:
- File list with real-time scanning
- Settings panel for source/target directories
- Progress tracking with live updates
- Results summary
- Preview mode

### Command Line Interface

Quick command-line usage:

```bash
# Basic usage (move files from ~/Desktop to ~/Desktop/Screenshots)
python main.py --cli

# Preview mode (see what will happen without moving files)
python main.py --cli --preview

# Copy instead of move
python main.py --cli --copy

# Custom directories
python main.py --cli --source ~/Downloads --target ~/Pictures/Screenshots

# Enable recursive scanning
python main.py --cli --recursive --source ~/Desktop/tmp
```

### Options

| Option | Description |
|--------|-------------|
| `--cli` | Use command line interface |
| `--source, -s` | Source directory (default: ~/Desktop) |
| `--target, -t` | Target directory (default: ~/Desktop/Screenshots) |
| `--preview, -p` | Preview mode - don't actually move files |
| `--copy, -c` | Copy files instead of moving them |
| `--recursive, -r` | Search subdirectories recursively |
| `--pattern` | Custom regex pattern for matching files |

## Folder Structure

Screenshots are organized into this structure:

```
Screenshots/
├── 2025-07-July/
│   ├── Week30/
│   │   └── Screenshot 2025-07-24 at 22.37.04.png
│   └── Week31/
│       └── Screenshot 2025-07-25 at 10.15.33.png
├── 2025-08-August/
│   └── Week31/
│       └── Screenshot 2025-08-01 at 14.22.07.png
```

- **Year-Month-Name**: Groups by month for easy browsing
- **Week folders**: Prevents too many files in one folder
- **ISO week numbers**: Consistent week numbering system

## Examples

```bash
# Organize all screenshots on desktop
python main.py --cli

# Preview what would happen first
python main.py --cli --preview

# Process files from Downloads folder
python main.py --cli --source ~/Downloads --target ~/Pictures/Organized

# Clean up scattered screenshots recursively
python main.py --cli --recursive --source ~/Desktop/tmp --preview
```

## File Support

Supports common screenshot formats:
- `.png` (primary macOS screenshot format)
- `.jpg`, `.jpeg`
- `.gif`, `.bmp`, `.tiff`, `.webp`

## Requirements

- Python 3.13+
- Textual (for TUI interface)