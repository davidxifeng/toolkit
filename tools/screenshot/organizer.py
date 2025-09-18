"""
Screenshot Organizer - Core functionality
Organizes screenshot files by date into year/month folder structure.
"""

import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Callable
from dataclasses import dataclass
from enum import Enum


class OperationMode(Enum):
    MOVE = "move"
    OPTIMIZE_MOVE = "optimize_move"


@dataclass
class ProcessResult:
    """Result of processing a single file"""
    source_path: Path
    target_path: Optional[Path]
    success: bool
    error_message: Optional[str] = None
    original_size: Optional[int] = None
    compressed_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    optimization_time: Optional[float] = None
    pngquant_status: Optional[str] = None


@dataclass
class OrganizeResult:
    """Result of organizing operation"""
    total_files: int
    processed_files: int
    failed_files: int
    created_folders: List[Path]
    results: List[ProcessResult]
    total_original_size: int = 0
    total_compressed_size: int = 0
    total_savings: int = 0
    optimization_stats: Optional[Dict] = None


class ScreenshotOrganizer:
    """Core screenshot organization functionality"""
    
    # Default pattern for screenshot files
    DEFAULT_PATTERN = r"Screenshot (\d{4})-(\d{2})-(\d{2}) at"
    # Default extensions for screenshot files
    DEFAULT_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    
    def __init__(
        self,
        source_dir: Optional[Path] = None,
        target_dir: Optional[Path] = None,
        pattern: Optional[str] = None,
        mode: OperationMode = OperationMode.OPTIMIZE_MOVE,
        recursive: bool = False,
        extensions: Optional[set] = None,
        keep_original: bool = False
    ):
        self.source_dir = source_dir or Path.home() / "Desktop"
        self.target_dir = target_dir or Path.home() / "Desktop" / "Screenshots"
        self.pattern = pattern or self.DEFAULT_PATTERN
        self.mode = mode
        self.recursive = recursive
        self.extensions = extensions or self.DEFAULT_EXTENSIONS
        self.keep_original = keep_original
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

    def _optimize_with_pngquant(self, source_path: Path, target_path: Path) -> ProcessResult:
        """Optimize PNG file with pngquant and move to target location"""
        start_time = time.time()
        original_size = source_path.stat().st_size

        # Only optimize PNG files
        if source_path.suffix.lower() != '.png':
            # For non-PNG files, just move them
            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                if self.keep_original:
                    shutil.copy2(source_path, target_path)
                else:
                    shutil.move(str(source_path), str(target_path))

                return ProcessResult(
                    source_path=source_path,
                    target_path=target_path,
                    success=True,
                    original_size=original_size,
                    compressed_size=original_size,
                    compression_ratio=0.0,
                    optimization_time=time.time() - start_time,
                    pngquant_status="skipped_non_png"
                )
            except Exception as e:
                return ProcessResult(
                    source_path=source_path,
                    target_path=target_path,
                    success=False,
                    error_message=str(e),
                    original_size=original_size,
                    optimization_time=time.time() - start_time,
                    pngquant_status="error"
                )

        # Create temporary file for optimization
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = Path(tmp_file.name)

        try:
            # Copy original to temp location for pngquant processing
            shutil.copy2(source_path, temp_path)

            # Run pngquant optimization
            cmd = ['pngquant', '--force', '--ext', '.png', '--skip-if-larger', str(temp_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)

            if result.returncode == 0:
                # Optimization successful
                compressed_size = temp_path.stat().st_size
                compression_ratio = (original_size - compressed_size) / original_size * 100 if original_size > 0 else 0

                # Move optimized file to target
                shutil.move(str(temp_path), str(target_path))

                # Remove original file if not keeping it
                if not self.keep_original:
                    source_path.unlink()

                return ProcessResult(
                    source_path=source_path,
                    target_path=target_path,
                    success=True,
                    original_size=original_size,
                    compressed_size=compressed_size,
                    compression_ratio=compression_ratio,
                    optimization_time=time.time() - start_time,
                    pngquant_status="optimized"
                )
            else:
                # Optimization failed or skipped, fall back to regular move
                shutil.move(str(temp_path), str(target_path))

                # Remove original file if not keeping it
                if not self.keep_original:
                    source_path.unlink()

                return ProcessResult(
                    source_path=source_path,
                    target_path=target_path,
                    success=True,
                    original_size=original_size,
                    compressed_size=original_size,
                    compression_ratio=0.0,
                    optimization_time=time.time() - start_time,
                    pngquant_status="skipped_larger"
                )

        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()

            # Fall back to regular move on error
            try:
                if self.keep_original:
                    shutil.copy2(source_path, target_path)
                else:
                    shutil.move(str(source_path), str(target_path))

                return ProcessResult(
                    source_path=source_path,
                    target_path=target_path,
                    success=True,
                    original_size=original_size,
                    compressed_size=original_size,
                    compression_ratio=0.0,
                    optimization_time=time.time() - start_time,
                    pngquant_status="error_fallback",
                    error_message=f"Optimization failed, fallback successful: {str(e)}"
                )
            except Exception as fallback_error:
                return ProcessResult(
                    source_path=source_path,
                    target_path=target_path,
                    success=False,
                    original_size=original_size,
                    optimization_time=time.time() - start_time,
                    pngquant_status="error",
                    error_message=f"Both optimization and fallback failed: {str(fallback_error)}"
                )

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
                
            # Process file with optimization or regular move
            if self.mode == OperationMode.OPTIMIZE_MOVE:
                result = self._optimize_with_pngquant(file_path, target_path)
            else:
                # Fallback to regular move
                try:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(target_path))
                    original_size = file_path.stat().st_size
                    result = ProcessResult(
                        source_path=file_path,
                        target_path=target_path,
                        success=True,
                        original_size=original_size,
                        compressed_size=original_size,
                        compression_ratio=0.0,
                        pngquant_status="move_only"
                    )
                except Exception as e:
                    result = ProcessResult(
                        source_path=file_path,
                        target_path=target_path,
                        success=False,
                        error_message=str(e),
                        pngquant_status="error"
                    )

            results.append(result)
            created_folders.add(target_path.parent)

            if result.success:
                processed += 1
            else:
                failed += 1
        
        # Calculate compression statistics
        total_original_size = sum(r.original_size for r in results if r.original_size)
        total_compressed_size = sum(r.compressed_size for r in results if r.compressed_size)
        total_savings = total_original_size - total_compressed_size

        optimization_stats = {
            "optimized_count": sum(1 for r in results if r.pngquant_status == "optimized"),
            "skipped_non_png": sum(1 for r in results if r.pngquant_status == "skipped_non_png"),
            "skipped_larger": sum(1 for r in results if r.pngquant_status == "skipped_larger"),
            "error_count": sum(1 for r in results if r.pngquant_status and "error" in r.pngquant_status),
            "average_compression": (total_savings / total_original_size * 100) if total_original_size > 0 else 0
        }

        return OrganizeResult(
            total_files=len(files),
            processed_files=processed,
            failed_files=failed,
            created_folders=list(created_folders),
            results=results,
            total_original_size=total_original_size,
            total_compressed_size=total_compressed_size,
            total_savings=total_savings,
            optimization_stats=optimization_stats
        )

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB"]
        unit_index = 0
        size = float(size_bytes)

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"

    def generate_compression_report(self, result: OrganizeResult) -> str:
        """Generate detailed compression statistics report"""
        if not result.optimization_stats:
            return "No optimization statistics available."

        stats = result.optimization_stats

        report = f"""
🎯 截图整理完成报告
====================================
📁 处理概况:
   • 总文件数: {result.total_files} 个
   • 成功处理: {result.processed_files} 个
   • 失败文件: {result.failed_files} 个

💾 存储优化:
   • 原始总大小: {self._format_size(result.total_original_size)} {'(已删除)' if not self.keep_original else '(已保留)'}
   • 压缩后大小: {self._format_size(result.total_compressed_size)}
   • 节省空间: {self._format_size(result.total_savings)} ({stats['average_compression']:.1f}%)

⚡ 优化详情:
   • PNG优化成功: {stats['optimized_count']} 个文件
   • 非PNG文件: {stats['skipped_non_png']} 个文件
   • 跳过优化(文件变大): {stats['skipped_larger']} 个文件
   • 优化失败: {stats['error_count']} 个文件

📂 创建目录: {len(result.created_folders)} 个
"""

        # Add individual file details if there are any interesting cases
        interesting_files = [r for r in result.results if r.compression_ratio and r.compression_ratio > 50]
        if interesting_files:
            report += "\n🏆 最佳压缩效果 (前5个):\n"
            sorted_files = sorted(interesting_files, key=lambda x: x.compression_ratio or 0, reverse=True)[:5]
            for r in sorted_files:
                report += f"   • {r.source_path.name}: {r.compression_ratio:.1f}% "
                report += f"({self._format_size(r.original_size or 0)} → {self._format_size(r.compressed_size or 0)})\n"

        return report.strip()


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
    parser.add_argument("--keep-original", action="store_true",
                       help="Keep original files after optimization (don't delete)")
    parser.add_argument("--pattern", type=str,
                       help="Custom regex pattern for matching files")
    parser.add_argument("--recursive", "-r", action="store_true",
                       help="Search subdirectories recursively")
    
    args = parser.parse_args()
    
    # Create organizer - always use OPTIMIZE_MOVE mode by default
    organizer = ScreenshotOrganizer(
        source_dir=args.source,
        target_dir=args.target,
        pattern=args.pattern,
        mode=OperationMode.OPTIMIZE_MOVE,
        recursive=args.recursive,
        keep_original=args.keep_original
    )
    
    # Set up progress callback
    def print_progress(current: int, total: int, filename: str):
        print(f"Processing {current}/{total}: {filename}")
    
    organizer.set_progress_callback(print_progress)
    
    # Run organization
    print(f"Organizing screenshots from {organizer.source_dir}")
    print(f"Target directory: {organizer.target_dir}")
    print(f"Mode: OPTIMIZE_MOVE (with PNG compression)")
    print(f"Keep original files: {'Yes' if args.keep_original else 'No'}")

    if args.preview:
        print("\n--- PREVIEW MODE ---")

    result = organizer.organize_files(preview_only=args.preview)

    # Print detailed compression report
    if not args.preview:
        print(organizer.generate_compression_report(result))
    else:
        # Simple preview results
        print(f"\nPreview Results:")
        print(f"Total files found: {result.total_files}")
        print(f"Would be processed: {result.processed_files}")
        print(f"Invalid files: {result.failed_files}")

        if result.created_folders:
            print(f"\nWould create folders:")
            for folder in sorted(result.created_folders):
                print(f"  {folder}")

    if result.failed_files > 0:
        print(f"\nFailed files:")
        for res in result.results:
            if not res.success:
                print(f"  {res.source_path}: {res.error_message}")


if __name__ == "__main__":
    main()