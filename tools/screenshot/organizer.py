"""
Screenshot Organizer - Core functionality
Organizes screenshot files by date into year/month folder structure.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Callable
from dataclasses import dataclass
from enum import Enum


class OperationMode(Enum):
    MOVE = "move"
    COPY = "copy"


@dataclass
class ProcessResult:
    """Result of processing a single file"""
    source_path: Path
    target_path: Path
    success: bool
    error_message: Optional[str] = None


@dataclass
class OrganizeResult:
    """Result of organizing operation"""
    total_files: int
    processed_files: int
    failed_files: int
    created_folders: List[Path]
    results: List[ProcessResult]


class ScreenshotOrganizer:
    """Core screenshot organization functionality"""
    
    # Default pattern for screenshot files
    DEFAULT_PATTERN = r"Screenshot (\d{4})-(\d{2})-(\d{2}) at"
    # Default extensions for screenshot files
    DEFAULT_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    
    def __init__(
        self,
        source_dir: Path = None,
        target_dir: Path = None,
        pattern: str = None,
        mode: OperationMode = OperationMode.MOVE,
        recursive: bool = False,
        extensions: set = None
    ):
        self.source_dir = source_dir or Path.home() / "Desktop"
        self.target_dir = target_dir or Path.home() / "Desktop" / "Screenshots"
        self.pattern = pattern or self.DEFAULT_PATTERN
        self.mode = mode
        self.recursive = recursive
        self.extensions = extensions or self.DEFAULT_EXTENSIONS
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None
        
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """Set callback for progress updates: callback(current, total, current_file)"""
        self.progress_callback = callback
        
    def find_screenshot_files(self) -> List[Path]:
        """Find all screenshot files matching the pattern"""
        files = []
        if not self.source_dir.exists():
            return files
        
        if self.recursive:
            # Recursively search all subdirectories
            for file_path in self.source_dir.rglob('*'):
                if (file_path.is_file() and 
                    self._matches_pattern(file_path.name) and
                    self._has_valid_extension(file_path)):
                    files.append(file_path)
        else:
            # Only search immediate directory
            for file_path in self.source_dir.iterdir():
                if (file_path.is_file() and 
                    self._matches_pattern(file_path.name) and
                    self._has_valid_extension(file_path)):
                    files.append(file_path)
                
        return sorted(files)
    
    def _matches_pattern(self, filename: str) -> bool:
        """Check if filename matches screenshot pattern"""
        return bool(re.search(self.pattern, filename))
    
    def _has_valid_extension(self, file_path: Path) -> bool:
        """Check if file has a valid screenshot extension"""
        return file_path.suffix.lower() in self.extensions
    
    def _parse_date_from_filename(self, filename: str) -> Optional[Tuple[int, int, int]]:
        """Parse year, month, day from filename"""
        match = re.search(self.pattern, filename)
        if match:
            year, month, day = match.groups()
            return int(year), int(month), int(day)
        return None
    
    def _get_month_name(self, month: int) -> str:
        """Get month name from month number"""
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return months[month - 1]
    
    def _get_week_of_year(self, year: int, month: int, day: int) -> int:
        """Get the week number of the year for a given date"""
        date = datetime(year, month, day)
        # Get ISO week number (Monday as first day of week)
        return date.isocalendar()[1]
    
    def _create_target_path(self, filename: str) -> Optional[Path]:
        """Create target path for file based on date"""
        date_info = self._parse_date_from_filename(filename)
        if not date_info:
            return None
            
        year, month, day = date_info
        week_num = self._get_week_of_year(year, month, day)
        month_name = self._get_month_name(month)
        
        # Format: YYYY-MM-MonthName/WeekNN/filename
        month_folder = f"{year}-{month:02d}-{month_name}"
        week_folder = f"Week{week_num:02d}"
        
        return self.target_dir / month_folder / week_folder / filename
    
    def preview_organization(self) -> Dict[str, List[Tuple[Path, Path]]]:
        """Preview what files will be organized where"""
        files = self.find_screenshot_files()
        preview = {"valid": [], "invalid": []}
        
        for file_path in files:
            target_path = self._create_target_path(file_path.name)
            if target_path:
                preview["valid"].append((file_path, target_path))
            else:
                preview["invalid"].append((file_path, None))
                
        return preview
    
    def organize_files(self, preview_only: bool = False) -> OrganizeResult:
        """Organize screenshot files"""
        files = self.find_screenshot_files()
        results = []
        created_folders = set()
        processed = 0
        failed = 0
        
        for i, file_path in enumerate(files):
            if self.progress_callback:
                self.progress_callback(i + 1, len(files), file_path.name)
                
            target_path = self._create_target_path(file_path.name)
            
            if not target_path:
                results.append(ProcessResult(
                    source_path=file_path,
                    target_path=None,
                    success=False,
                    error_message="Could not parse date from filename"
                ))
                failed += 1
                continue
            
            if preview_only:
                results.append(ProcessResult(
                    source_path=file_path,
                    target_path=target_path,
                    success=True
                ))
                created_folders.add(target_path.parent)
                processed += 1
                continue
                
            try:
                # Create target directory if it doesn't exist
                target_path.parent.mkdir(parents=True, exist_ok=True)
                created_folders.add(target_path.parent)
                
                # Move or copy file
                if self.mode == OperationMode.COPY:
                    shutil.copy2(file_path, target_path)
                else:
                    shutil.move(str(file_path), str(target_path))
                    
                results.append(ProcessResult(
                    source_path=file_path,
                    target_path=target_path,
                    success=True
                ))
                processed += 1
                
            except Exception as e:
                results.append(ProcessResult(
                    source_path=file_path,
                    target_path=target_path,
                    success=False,
                    error_message=str(e)
                ))
                failed += 1
        
        return OrganizeResult(
            total_files=len(files),
            processed_files=processed,
            failed_files=failed,
            created_folders=list(created_folders),
            results=results
        )


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize screenshot files by date")
    parser.add_argument("--source", "-s", type=Path, 
                       help="Source directory (default: ~/Desktop)")
    parser.add_argument("--target", "-t", type=Path,
                       help="Target directory (default: ~/Screenshots)")
    parser.add_argument("--preview", "-p", action="store_true",
                       help="Preview mode - don't actually move files")
    parser.add_argument("--copy", "-c", action="store_true",
                       help="Copy files instead of moving them")
    parser.add_argument("--pattern", type=str,
                       help="Custom regex pattern for matching files")
    parser.add_argument("--recursive", "-r", action="store_true",
                       help="Search subdirectories recursively")
    
    args = parser.parse_args()
    
    # Create organizer
    mode = OperationMode.COPY if args.copy else OperationMode.MOVE
    organizer = ScreenshotOrganizer(
        source_dir=args.source,
        target_dir=args.target,
        pattern=args.pattern,
        mode=mode,
        recursive=args.recursive
    )
    
    # Set up progress callback
    def print_progress(current: int, total: int, filename: str):
        print(f"Processing {current}/{total}: {filename}")
    
    organizer.set_progress_callback(print_progress)
    
    # Run organization
    print(f"Organizing screenshots from {organizer.source_dir}")
    print(f"Target directory: {organizer.target_dir}")
    print(f"Mode: {'COPY' if args.copy else 'MOVE'}")
    
    if args.preview:
        print("\n--- PREVIEW MODE ---")
        
    result = organizer.organize_files(preview_only=args.preview)
    
    # Print results
    print(f"\nResults:")
    print(f"Total files found: {result.total_files}")
    print(f"Successfully processed: {result.processed_files}")
    print(f"Failed: {result.failed_files}")
    
    if result.created_folders:
        print(f"\nCreated folders:")
        for folder in sorted(result.created_folders):
            print(f"  {folder}")
    
    if result.failed_files > 0:
        print(f"\nFailed files:")
        for res in result.results:
            if not res.success:
                print(f"  {res.source_path}: {res.error_message}")


if __name__ == "__main__":
    main()