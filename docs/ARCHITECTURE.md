# Toolkit 架构设计文档

本文档描述了 Toolkit 项目的整体架构设计、设计原则和实现细节。

## 🎯 设计目标

1. **模块化**: 每个工具独立开发和维护
2. **扩展性**: 轻松添加新工具而不影响现有功能
3. **多样化调用方式**: 支持交互式菜单、直接调用、独立脚本等
4. **用户友好**: 提供清晰的界面和文档
5. **开发友好**: 清晰的代码结构和开发指南

## 🏗️ 架构概述

```
┌─────────────────────────────────────────┐
│                用户界面层                │
├─────────────┬─────────────┬─────────────┤
│ 交互式菜单  │  直接调用   │  独立脚本   │
│   (TUI)     │   (CLI)     │  (Scripts)  │
└─────────────┴─────────────┴─────────────┘
                    │
┌─────────────────────────────────────────┐
│            主入口控制层 (main.py)        │
│  - 工具注册与发现                       │
│  - 参数解析与路由                       │
│  - 统一错误处理                         │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│              工具模块层                 │
├─────────────────┬───────────────────────┤
│  tools/         │                       │
│  ├─screenshot/  │  ├─image/             │
│  │  ├─organizer │  │  └─reorganizer     │
│  │  └─tui       │  │                    │
│  └─[future]/    │  └─[future]/          │
└─────────────────┴───────────────────────┘
                    │
┌─────────────────────────────────────────┐
│              基础设施层                 │
│  - 配置管理 (pyproject.toml)           │
│  - 测试框架 (tests/)                   │
│  - 文档系统 (docs/)                    │
│  - 脚本支持 (scripts/)                 │
└─────────────────────────────────────────┘
```

## 📁 目录结构设计

### 核心文件

```
toolkit/
├── main.py                 # 主入口和工具路由器
├── pyproject.toml         # 项目配置和依赖管理
└── README.md              # 用户文档
```

### 工具模块

```
tools/                     # 工具模块根目录
├── __init__.py           # 包初始化
├── screenshot/           # 截图工具模块
│   ├── __init__.py      # 模块导出定义
│   ├── organizer.py     # CLI 实现
│   └── tui.py           # TUI 实现
└── image/               # 图片工具模块
    ├── __init__.py      # 模块导出定义
    └── reorganizer.py   # 核心实现
```

### 支持文件

```
scripts/                  # 独立可执行脚本
├── toolkit              # 主工具入口
├── screenshot-org       # 截图工具脚本
└── image-reorg         # 图片工具脚本

tests/                   # 测试目录
├── test_screenshot/     # 截图工具测试
└── test_image/         # 图片工具测试

docs/                    # 文档目录
├── ARCHITECTURE.md     # 架构文档
├── DEVELOPMENT.md      # 开发指南
└── CHANGELOG.md        # 变更日志
```

## 🔧 核心组件详解

### 1. 主入口控制器 (main.py)

主入口负责：
- **工具注册**: 通过 `list_available_tools()` 维护工具注册表
- **参数路由**: 解析用户输入并路由到相应工具
- **界面选择**: 提供交互式菜单或直接调用
- **错误处理**: 统一的错误处理和用户反馈

```python
def list_available_tools():
    """工具注册表 - 添加新工具时在这里注册"""
    return {
        "screenshot": {
            "name": "Screenshot Organizer",
            "description": "...",
            "module": "tools.screenshot"
        },
        "image": {
            "name": "Image Reorganizer",
            "description": "...", 
            "module": "tools.image.reorganizer"
        }
    }
```

### 2. 工具模块设计

每个工具模块遵循统一的设计模式：

#### 模块结构
- `__init__.py`: 定义模块导出和元数据
- `main.py` 或具体实现文件: 核心工具逻辑
- 可选：`tui.py`, `cli.py` 等不同界面实现

#### 工具类设计
```python
class ToolClass:
    def __init__(self):
        self.config = {}
    
    def run(self, args):
        """主要执行方法"""
        pass
    
def main():
    """CLI 入口点"""
    parser = argparse.ArgumentParser()
    # ... 参数解析
    tool = ToolClass()
    tool.run(args)
```

### 3. 脚本系统

独立脚本提供：
- **直接执行**: 无需通过 main.py 调用
- **路径处理**: 自动处理 Python 模块路径
- **参数传递**: 透明地传递命令行参数

脚本模板：
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# 添加工具包目录到 Python 路径
toolkit_dir = Path(__file__).parent.parent
sys.path.insert(0, str(toolkit_dir))

from tools.your_tool.main import main

if __name__ == "__main__":
    main()
```

## 🔄 工作流程

### 1. 交互式菜单流程

```
用户运行: python main.py
    ↓
main.py 显示工具菜单
    ↓
用户选择工具
    ↓
main.py 调用对应工具的运行函数
    ↓
工具执行并返回结果
```

### 2. 直接调用流程

```
用户运行: python main.py screenshot --cli
    ↓
main.py 解析参数识别工具和参数
    ↓
直接调用 run_screenshot_tool(args)
    ↓
设置 sys.argv 并调用工具的 main()
```

### 3. 独立脚本流程

```
用户运行: ./scripts/screenshot-org --help
    ↓
脚本设置 Python 路径
    ↓
直接导入并调用工具的 main()
```

## 🎨 设计模式

### 1. 插件模式
每个工具都是一个独立的插件，通过工具注册表进行管理。

### 2. 工厂模式
主入口根据用户选择创建相应的工具实例。

### 3. 策略模式
每个工具可以有多种执行策略（CLI、TUI 等）。

### 4. 命令模式
将用户的操作请求封装为命令对象。

## 🔌 扩展机制

### 添加新工具的步骤

1. **创建工具目录**:
   ```bash
   mkdir tools/new_tool
   ```

2. **实现工具类**:
   ```python
   # tools/new_tool/main.py
   class NewTool:
       def run(self, args): pass
   
   def main(): pass
   ```

3. **注册工具**:
   在 `main.py` 的工具注册表中添加条目

4. **添加路由函数**:
   ```python
   def run_new_tool(args):
       from tools.new_tool.main import main
       main()
   ```

5. **更新主控制逻辑**:
   在 `main()` 函数中添加工具调用分支

### 工具接口规范

每个工具应该提供：
- **main()** 函数作为 CLI 入口
- **help** 参数支持
- **错误处理**和有意义的返回码
- **进度反馈**（对于长时间运行的任务）

## 🧪 测试架构

### 测试组织
```
tests/
├── __init__.py
├── test_main.py          # 主入口测试
├── test_screenshot/      # 截图工具测试
│   └── test_organizer.py
└── test_image/          # 图片工具测试
    └── test_reorganizer.py
```

### 测试类型
- **单元测试**: 测试individual组件功能
- **集成测试**: 测试工具间协作
- **端到端测试**: 测试完整用户流程

## 📋 配置管理

### pyproject.toml 结构
```toml
[project]
# 项目元数据

[project.scripts]
# 可执行脚本入口点

[project.optional-dependencies]
# 开发依赖
```

### 配置优先级
1. 命令行参数
2. 环境变量
3. 配置文件
4. 默认值

## 🚀 性能考虑

### 懒加载
- 工具模块按需导入
- 重依赖（如 Pillow, Textual）延迟加载

### 内存管理
- 大文件处理时使用流式处理
- 及时释放不需要的资源

### 并发处理
- 支持多线程/异步处理（适用的工具）
- 进度反馈和取消机制

## 🔒 错误处理策略

### 错误分类
1. **用户错误**: 无效参数、文件不存在等
2. **系统错误**: 权限问题、磁盘空间等
3. **程序错误**: 代码 bug、未处理异常

### 处理原则
- **优雅降级**: 部分失败时继续处理其他任务
- **清晰反馈**: 提供有用的错误信息和建议
- **日志记录**: 详细记录错误用于调试

## 📈 未来扩展方向

### 短期目标
- 添加更多实用工具
- 改进用户界面
- 增加配置文件支持

### 长期目标
- 插件市场/注册机制
- Web 界面支持
- 远程工具执行
- 工具链和工作流支持

---

本架构文档会随着项目发展持续更新。如有架构相关问题或建议，请提交 Issue 讨论。