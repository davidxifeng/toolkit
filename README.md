# 截图整理工具

[English](README.en.md) | 中文

一个简单的工具，可以按日期自动整理截图文件到清晰的文件夹结构中。

## 功能特性

- **智能整理**: 自动将截图分类到 `YYYY-MM-月份名/第NN周/` 文件夹中
- **精美界面**: 基于 Textual 构建的交互式终端界面
- **快速命令行**: 支持自动化和脚本的命令行界面
- **模式识别**: 识别 macOS 截图格式: `Screenshot YYYY-MM-DD at HH.MM.SS.png`
- **灵活选项**: 移动或复制文件，处理前预览
- **智能过滤**: 只处理有效的图像文件 (.png, .jpg, .jpeg 等)

## 安装

```bash
# 安装依赖
uv sync

# 或使用 pip
pip install textual
```

## 使用方法

### TUI 界面（默认）

启动交互式终端界面：

```bash
python main.py
```

功能特性：
- 实时扫描的文件列表
- 源目录和目标目录设置面板
- 实时进度跟踪
- 结果摘要
- 预览模式

### 命令行界面

快速命令行使用：

```bash
# 基本用法（将文件从 ~/Desktop 移动到 ~/Desktop/Screenshots）
python main.py --cli

# 预览模式（查看将要执行的操作但不实际移动文件）
python main.py --cli --preview

# 复制而不是移动
python main.py --cli --copy

# 自定义目录
python main.py --cli --source ~/Downloads --target ~/Pictures/Screenshots

# 启用递归扫描
python main.py --cli --recursive --source ~/Desktop/tmp
```

### 选项说明

| 选项 | 说明 |
|------|------|
| `--cli` | 使用命令行界面 |
| `--source, -s` | 源目录（默认: ~/Desktop） |
| `--target, -t` | 目标目录（默认: ~/Desktop/Screenshots） |
| `--preview, -p` | 预览模式 - 不实际移动文件 |
| `--copy, -c` | 复制文件而不是移动 |
| `--recursive, -r` | 递归搜索子目录 |
| `--pattern` | 自定义文件匹配正则表达式 |

## 文件夹结构

截图会被整理成这样的结构：

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

- **年-月-月份名**: 按月分组便于浏览
- **周文件夹**: 防止单个文件夹文件过多
- **ISO 周数**: 一致的周数编号系统

## 使用示例

```bash
# 整理桌面上的所有截图
python main.py --cli

# 先预览将要执行的操作
python main.py --cli --preview

# 处理下载文件夹中的文件
python main.py --cli --source ~/Downloads --target ~/Pictures/Organized

# 递归清理分散的截图
python main.py --cli --recursive --source ~/Desktop/tmp --preview
```

## 支持的文件格式

支持常见的截图格式：
- `.png`（macOS 主要截图格式）
- `.jpg`, `.jpeg`
- `.gif`, `.bmp`, `.tiff`, `.webp`

## 系统要求

- Python 3.13+
- Textual（用于 TUI 界面）