# Toolkit - 日常系统工具箱

[English](README.en.md) | 中文

一个模块化的工具集合，包含多种日常系统实用工具。支持交互式菜单、直接调用和独立脚本等多种使用方式。

## 🧰 包含的工具

### 1. 截图整理工具 (Screenshot Organizer)
自动按日期整理截图文件到清晰的文件夹结构中。

**功能特性：**
- **智能整理**: 自动将截图分类到 `YYYY-MM-月份名/第NN周/` 文件夹中
- **精美界面**: 基于 Textual 构建的交互式终端界面 (TUI)
- **快速命令行**: 支持自动化和脚本的命令行界面 (CLI)
- **模式识别**: 识别 macOS 截图格式: `Screenshot YYYY-MM-DD at HH.MM.SS.png`
- **灵活选项**: 移动或复制文件，处理前预览

### 2. 图片重组工具 (Image Reorganizer)  
将水平拼接的图片转换为 2D 网格布局。

**功能特性：**
- **智能布局**: 自动计算最佳的网格布局（最接近正方形）
- **灵活缩放**: 支持输出图片缩放
- **批量处理**: 可处理任意数量的子图片
- **多种选项**: 自定义子图片宽度、输出路径等

## 🚀 安装

```bash
# 克隆仓库
git clone <repository-url>
cd toolkit

# 安装依赖
uv sync
# 或使用 pip
pip install -r requirements.txt

# 可选：安装为可执行包
pip install -e .
```

## 📖 使用方法

### 方式 1: 交互式菜单（推荐）

启动主工具选择菜单：

```bash
python main.py
```

这会显示一个友好的菜单界面，让你选择要使用的工具。

### 方式 2: 直接调用特定工具

```bash
# 查看所有可用工具
python main.py --help

# 运行截图整理工具
python main.py screenshot --help          # 查看帮助
python main.py screenshot --tui           # TUI 界面
python main.py screenshot --cli --preview # CLI 预览模式

# 运行图片重组工具
python main.py image input.png --help     # 查看帮助
python main.py image input.png --scale 0.5 --output result.png
```

### 方式 3: 独立脚本

```bash
# 使用独立脚本（需要先 chmod +x scripts/*）
./scripts/toolkit                    # 主菜单
./scripts/screenshot-org --help      # 截图工具
./scripts/image-reorg input.png      # 图片工具
```

### 方式 4: 全局安装（可选）

```bash
# 安装后全局使用
pip install -e .

# 然后可以在任何地方直接调用
toolkit
screenshot-org --help
image-reorg input.png
```

## 🛠️ 工具详细用法

### 截图整理工具

#### TUI 界面（交互式）
```bash
python main.py screenshot --tui
```
功能包括：
- 实时文件扫描和预览
- 源/目标目录设置面板  
- 进度跟踪和结果摘要

#### CLI 界面（命令行）
```bash
# 基本整理（Desktop -> Desktop/Screenshots）
python main.py screenshot --cli

# 预览模式（查看操作但不执行）
python main.py screenshot --cli --preview

# 复制而非移动文件
python main.py screenshot --cli --copy

# 自定义目录
python main.py screenshot --cli --source ~/Downloads --target ~/Pictures/Screenshots

# 递归扫描子目录
python main.py screenshot --cli --recursive
```

**整理后的文件夹结构：**
```
Screenshots/
├── 2025-01-January/
│   ├── Week01/
│   │   └── Screenshot 2025-01-05 at 10.30.15.png
│   └── Week02/
│       └── Screenshot 2025-01-08 at 14.22.33.png
└── 2025-02-February/
    └── Week06/
        └── Screenshot 2025-02-10 at 09.45.21.png
```

### 图片重组工具

```bash
# 基本用法（使用默认设置）
python main.py image input_horizontal_strip.png

# 指定子图片宽度
python main.py image input.png --sub-width 100

# 缩放输出图片
python main.py image input.png --scale 0.5

# 自定义输出路径
python main.py image input.png --output custom_grid.png

# 显示所有布局选项
python main.py image input.png --show-layouts
```

**示例：** 将一个包含 6 个正方形子图片的水平条状图片重组为 2x3 或 3x2 的网格。

## 📁 项目结构

```
toolkit/
├── README.md              # 主文档
├── main.py               # 主入口和工具选择器
├── pyproject.toml        # 项目配置
├── tools/                # 工具模块目录
│   ├── screenshot/       # 截图相关工具
│   │   ├── organizer.py  # CLI 实现
│   │   └── tui.py       # TUI 实现
│   └── image/           # 图片处理工具
│       └── reorganizer.py # 图片重组实现
├── scripts/             # 独立可执行脚本
│   ├── toolkit         # 主工具入口
│   ├── screenshot-org  # 截图工具脚本
│   └── image-reorg     # 图片工具脚本
├── tests/              # 测试目录
│   ├── test_screenshot/
│   └── test_image/
└── docs/               # 文档目录
```

## 🔧 开发指南

### 添加新工具

1. **创建工具模块**：
   ```bash
   mkdir tools/your_tool
   touch tools/your_tool/__init__.py
   touch tools/your_tool/main.py
   ```

2. **实现工具类**：
   ```python
   # tools/your_tool/main.py
   class YourTool:
       def __init__(self):
           pass
       
       def run(self, args):
           # 工具逻辑
           pass
   
   def main():
       # CLI 入口点
       pass
   ```

3. **注册到主入口**：
   在 `main.py` 的 `list_available_tools()` 中添加：
   ```python
   "your_tool": {
       "name": "Your Tool Name",
       "description": "Tool description",
       "module": "tools.your_tool.main"
   }
   ```

4. **添加运行函数**：
   ```python
   def run_your_tool(args):
       from tools.your_tool.main import main as tool_main
       sys.argv = ["your_tool"] + (args or [])
       tool_main()
   ```

5. **创建独立脚本**（可选）：
   ```bash
   # scripts/your-tool
   #!/usr/bin/env python3
   import sys
   from pathlib import Path
   
   toolkit_dir = Path(__file__).parent.parent
   sys.path.insert(0, str(toolkit_dir))
   
   from tools.your_tool.main import main
   
   if __name__ == "__main__":
       main()
   ```

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定工具的测试
python -m pytest tests/test_image/

# 生成覆盖率报告
python -m pytest --cov=tools tests/
```

## 📋 支持的文件格式

### 截图工具
- `.png` (macOS 主要截图格式)
- `.jpg`, `.jpeg`  
- `.gif`, `.bmp`, `.tiff`, `.webp`

### 图片工具
- 所有 PIL/Pillow 支持的格式
- 主要：`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`

## ⚙️ 系统要求

- Python 3.8+
- 依赖包：
  - `textual>=0.45.0` (TUI 界面)
  - `pillow>=9.0.0` (图片处理)

## 🤝 贡献

欢迎贡献新的工具和改进！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/new-tool`)
3. 提交更改 (`git commit -am 'Add new tool'`)
4. 推送分支 (`git push origin feature/new-tool`)
5. 创建 Pull Request

## 📄 许可证

MIT License

## 🆘 故障排除

### 常见问题

1. **导入错误**：确保已安装所有依赖包
2. **权限错误**：给脚本文件添加执行权限 `chmod +x scripts/*`
3. **模块未找到**：检查 Python 路径设置

### 获取帮助

- 查看具体工具帮助：`python main.py <tool> --help`
- 查看项目文档：`docs/` 目录
- 提交 Issue：在 GitHub 仓库中报告问题