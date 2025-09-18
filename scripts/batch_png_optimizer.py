#!/usr/bin/env python3
"""
Batch PNG Optimizer - 批量PNG文件优化工具
使用pngquant递归优化指定目录下的所有PNG文件
"""

import argparse
import subprocess
import tempfile
import time
import shutil
from pathlib import Path
from typing import List, Tuple


class PNGOptimizer:
    """PNG文件批量优化器"""

    def __init__(self, keep_original: bool = False, verbose: bool = True, recursive: bool = True):
        self.keep_original = keep_original
        self.verbose = verbose
        self.recursive = recursive
        self.processed_files = 0
        self.optimized_files = 0
        self.skipped_files = 0
        self.error_files = 0
        self.total_original_size = 0
        self.total_compressed_size = 0

    def find_png_files(self, directory: Path) -> List[Path]:
        """查找PNG文件（可选择是否递归）"""
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        if self.recursive:
            png_files = list(directory.rglob("*.png"))
            search_mode = "recursively"
        else:
            png_files = list(directory.glob("*.png"))
            search_mode = "in current directory only"

        if self.verbose:
            print(f"Found {len(png_files)} PNG files {search_mode} in {directory}")

        return png_files

    def optimize_png(self, file_path: Path) -> Tuple[bool, str, int, int]:
        """
        优化单个PNG文件

        Returns:
            (success, status_message, original_size, compressed_size)
        """
        try:
            original_size = file_path.stat().st_size

            # 创建临时文件进行优化
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_path = Path(tmp_file.name)

            try:
                # 复制原文件到临时位置
                shutil.copy2(file_path, temp_path)

                # 运行pngquant优化
                cmd = ['pngquant', '--force', '--ext', '.png', '--skip-if-larger', str(temp_path)]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    # 优化成功
                    compressed_size = temp_path.stat().st_size
                    compression_ratio = (original_size - compressed_size) / original_size * 100

                    if not self.keep_original:
                        # 替换原文件
                        shutil.move(str(temp_path), str(file_path))
                        status = f"optimized ({compression_ratio:.1f}% reduction)"
                    else:
                        # 保存为新文件
                        backup_path = file_path.with_suffix('.optimized.png')
                        shutil.move(str(temp_path), str(backup_path))
                        status = f"optimized to {backup_path.name} ({compression_ratio:.1f}% reduction)"

                    return True, status, original_size, compressed_size

                elif result.returncode == 98:
                    # 跳过，因为优化后文件更大
                    temp_path.unlink()
                    return True, "skipped (would be larger)", original_size, original_size

                else:
                    # pngquant失败
                    temp_path.unlink()
                    return False, f"pngquant failed: {result.stderr.strip()}", original_size, original_size

            except Exception as e:
                # 清理临时文件
                if temp_path.exists():
                    temp_path.unlink()
                return False, f"processing error: {str(e)}", original_size, original_size

        except Exception as e:
            return False, f"file access error: {str(e)}", 0, 0

    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
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

    def process_directory(self, directory: Path) -> None:
        """处理目录中的所有PNG文件"""
        print(f"🔍 Scanning directory: {directory}")

        try:
            png_files = self.find_png_files(directory)
        except (FileNotFoundError, ValueError) as e:
            print(f"❌ Error: {e}")
            return

        if not png_files:
            print("ℹ️  No PNG files found.")
            return

        print(f"📁 Processing {len(png_files)} PNG files...")
        print(f"🔄 Recursive mode: {'Yes' if self.recursive else 'No'}")
        print(f"💾 Keep original files: {'Yes' if self.keep_original else 'No'}")
        print("=" * 60)

        start_time = time.time()

        for i, file_path in enumerate(png_files, 1):
            if self.verbose:
                print(f"[{i}/{len(png_files)}] Processing {file_path.name}...", end=" ")

            success, status, original_size, compressed_size = self.optimize_png(file_path)

            self.processed_files += 1
            self.total_original_size += original_size
            self.total_compressed_size += compressed_size

            if success:
                if "optimized" in status and "skipped" not in status:
                    self.optimized_files += 1
                elif "skipped" in status:
                    self.skipped_files += 1

                if self.verbose:
                    print(f"✅ {status}")
            else:
                self.error_files += 1
                if self.verbose:
                    print(f"❌ {status}")

        end_time = time.time()
        self.print_summary(end_time - start_time)

    def print_summary(self, processing_time: float) -> None:
        """打印处理结果摘要"""
        print("=" * 60)
        print("🎯 批量PNG优化完成报告")
        print("=" * 60)

        print(f"📊 处理统计:")
        print(f"   • 总文件数: {self.processed_files}")
        print(f"   • 优化成功: {self.optimized_files}")
        print(f"   • 跳过优化: {self.skipped_files}")
        print(f"   • 处理失败: {self.error_files}")

        print(f"\n💾 存储优化:")
        print(f"   • 原始总大小: {self.format_size(self.total_original_size)}")
        print(f"   • 压缩后大小: {self.format_size(self.total_compressed_size)}")

        total_savings = self.total_original_size - self.total_compressed_size
        if self.total_original_size > 0:
            savings_percent = (total_savings / self.total_original_size) * 100
            print(f"   • 节省空间: {self.format_size(total_savings)} ({savings_percent:.1f}%)")
        else:
            print(f"   • 节省空间: 0 B (0%)")

        print(f"\n⏱️  处理时间: {processing_time:.2f} 秒")

        if self.optimized_files > 0:
            avg_time = processing_time / self.processed_files
            print(f"   • 平均每文件: {avg_time:.2f} 秒")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="批量PNG文件优化工具 - 使用pngquant优化目录中的PNG文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python batch_png_optimizer.py ~/Pictures               # 递归优化Pictures目录
  python batch_png_optimizer.py . --keep-original        # 优化当前目录并保留原文件
  python batch_png_optimizer.py /path/to/images -q       # 静默模式优化
  python batch_png_optimizer.py ~/Pictures --no-recursive # 只优化指定目录，不处理子目录
        """
    )

    parser.add_argument(
        "directory",
        type=Path,
        help="要处理的目录路径"
    )

    parser.add_argument(
        "--keep-original", "-k",
        action="store_true",
        help="保留原文件，优化后的文件保存为 .optimized.png"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式，只显示最终结果"
    )

    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="只处理指定目录中的PNG文件，不处理子目录"
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version="PNG Batch Optimizer 1.0.0"
    )

    args = parser.parse_args()

    # 检查pngquant是否可用
    try:
        result = subprocess.run(['pngquant', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Error: pngquant not found or not working")
            print("   Please install pngquant: brew install pngquant")
            exit(1)
    except FileNotFoundError:
        print("❌ Error: pngquant not found")
        print("   Please install pngquant: brew install pngquant")
        exit(1)

    # 创建优化器并开始处理
    optimizer = PNGOptimizer(
        keep_original=args.keep_original,
        verbose=not args.quiet,
        recursive=args.recursive
    )

    try:
        optimizer.process_directory(args.directory)
    except KeyboardInterrupt:
        print("\n\n⚠️  处理被用户中断")
        if optimizer.processed_files > 0:
            print("部分处理结果:")
            optimizer.print_summary(0)
    except Exception as e:
        print(f"❌ 处理出错: {e}")
        exit(1)


if __name__ == "__main__":
    main()