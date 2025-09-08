# Toolkit 开发指南

本文档为开发者提供详细的开发指南，包括环境搭建、开发流程、代码规范等。

## 🚀 快速开始

### 环境准备

```bash
# 克隆仓库
git clone <repository-url>
cd toolkit

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
# 或使用 uv
uv sync

# 安装开发依赖
pip install -e .[dev]
```

### 验证安装

```bash
# 运行主程序
python main.py

# 运行测试
python -m pytest tests/

# 检查代码格式
black --check .
flake8 .
```

## 🛠️ 开发新工具

### 1. 创建工具模块

```bash
# 创建工具目录
mkdir tools/my_tool
touch tools/my_tool/__init__.py
touch tools/my_tool/main.py
```

### 2. 实现工具核心逻辑

编辑 `tools/my_tool/main.py`:

```python
#!/usr/bin/env python3
"""
My Tool - 工具描述
"""

import argparse
import sys
from pathlib import Path


class MyTool:
    """工具类的基本结构"""
    
    def __init__(self):
        self.verbose = True
        self.config = {}
    
    def process(self, input_path, output_path=None, **kwargs):
        """
        核心处理方法
        
        Args:
            input_path: 输入文件或目录
            output_path: 输出路径（可选）
            **kwargs: 其他配置参数
            
        Returns:
            处理结果或输出路径
            
        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 参数无效
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input path not found: {input_path}")
        
        # 核心处理逻辑
        if self.verbose:
            print(f"Processing {input_path}...")
        
        # ... 实现你的工具逻辑 ...
        
        if self.verbose:
            print("Processing completed!")
        
        return output_path
    
    def validate_args(self, args):
        """验证参数有效性"""
        if not args.input:
            raise ValueError("Input path is required")
        # ... 其他验证逻辑


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(
        description="My Tool - 工具描述",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tools.my_tool.main input.txt
  python -m tools.my_tool.main input.txt --output result.txt
        """
    )
    
    # 必需参数
    parser.add_argument("input", help="输入文件路径")
    
    # 可选参数
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="显示详细信息")
    parser.add_argument("--config", help="配置文件路径")
    
    # 工具特定参数
    parser.add_argument("--option1", type=int, default=100,
                       help="选项1描述 (默认: 100)")
    parser.add_argument("--flag", action="store_true",
                       help="布尔标志")
    
    args = parser.parse_args()
    
    # 创建工具实例
    tool = MyTool()
    tool.verbose = args.verbose
    
    try:
        # 验证参数
        tool.validate_args(args)
        
        # 执行处理
        result = tool.process(
            input_path=args.input,
            output_path=args.output,
            option1=args.option1,
            flag=args.flag
        )
        
        if result:
            print(f"Success! Output: {result}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 3. 更新模块初始化文件

编辑 `tools/my_tool/__init__.py`:

```python
"""
My Tool - 工具描述
"""

from .main import MyTool

__all__ = ["MyTool"]
```

### 4. 注册到主入口

编辑 `main.py`，在 `list_available_tools()` 中添加：

```python
def list_available_tools():
    tools = {
        # ... 现有工具 ...
        "my_tool": {
            "name": "My Tool",
            "description": "工具的简短描述",
            "module": "tools.my_tool.main"
        }
    }
    return tools
```

添加运行函数：

```python
def run_my_tool(args):
    """运行我的工具"""
    from tools.my_tool.main import main as my_tool_main
    sys.argv = ["my_tool"] + (args or [])
    my_tool_main()
```

在 `main()` 函数中添加调用分支：

```python
def main():
    # ... 现有代码 ...
    
    if not parsed_args.tool:
        # 交互模式处理
        if selected_tool == "my_tool":
            run_my_tool([])
    else:
        # 直接调用处理
        if parsed_args.tool == "my_tool":
            run_my_tool(all_tool_args)
```

### 5. 创建独立脚本（可选）

创建 `scripts/my-tool`:

```python
#!/usr/bin/env python3
"""
My Tool 独立脚本
"""
import sys
import os
from pathlib import Path

# 添加 toolkit 目录到 Python 路径
toolkit_dir = Path(__file__).parent.parent
sys.path.insert(0, str(toolkit_dir))

from tools.my_tool.main import main

if __name__ == "__main__":
    main()
```

给脚本添加执行权限：

```bash
chmod +x scripts/my-tool
```

### 6. 编写测试

创建 `tests/test_my_tool/`:

```bash
mkdir tests/test_my_tool
touch tests/test_my_tool/__init__.py
```

编辑 `tests/test_my_tool/test_main.py`:

```python
"""
My Tool 测试用例
"""

import unittest
import tempfile
from pathlib import Path

from tools.my_tool.main import MyTool


class TestMyTool(unittest.TestCase):
    """My Tool 测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.tool = MyTool()
        self.tool.verbose = False  # 测试时关闭详细输出
        
        # 创建临时测试文件
        self.temp_dir = tempfile.mkdtemp()
        self.test_input = Path(self.temp_dir) / "test_input.txt"
        self.test_input.write_text("test content")
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_basic_functionality(self):
        """测试基本功能"""
        result = self.tool.process(self.test_input)
        self.assertIsNotNone(result)
    
    def test_invalid_input(self):
        """测试无效输入"""
        with self.assertRaises(FileNotFoundError):
            self.tool.process("nonexistent_file.txt")
    
    def test_with_options(self):
        """测试带选项的处理"""
        result = self.tool.process(
            self.test_input, 
            option1=200,
            flag=True
        )
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
```

### 7. 更新配置文件

在 `pyproject.toml` 中添加新的脚本入口点：

```toml
[project.scripts]
toolkit = "main:main"
screenshot-org = "tools.screenshot.organizer:main"
image-reorg = "tools.image.reorganizer:main"
my-tool = "tools.my_tool.main:main"  # 新增这行
```

## 🧪 测试指南

### 测试类型

1. **单元测试**: 测试单个函数/方法
2. **集成测试**: 测试模块间协作
3. **端到端测试**: 测试完整用户流程

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_my_tool/

# 运行带覆盖率的测试
python -m pytest --cov=tools tests/

# 详细输出
python -m pytest -v tests/

# 只运行失败的测试
python -m pytest --lf
```

### 测试最佳实践

1. **测试文件命名**: `test_*.py`
2. **测试类命名**: `TestClassName`
3. **测试方法命名**: `test_method_name`
4. **使用临时文件**: 避免影响实际文件
5. **测试边界情况**: 空输入、大文件、权限错误等
6. **模拟外部依赖**: 使用 mock 避免网络调用等

### 测试示例模板

```python
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

class TestYourTool(unittest.TestCase):
    
    def setUp(self):
        """每个测试前的准备工作"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_file.write_text("test data")
    
    def tearDown(self):
        """每个测试后的清理工作"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_normal_case(self):
        """正常情况测试"""
        # 准备
        expected = "expected_result"
        
        # 执行
        result = your_function(self.test_file)
        
        # 验证
        self.assertEqual(result, expected)
    
    def test_edge_case(self):
        """边界情况测试"""
        with self.assertRaises(ValueError):
            your_function(None)
    
    @patch('your_module.external_function')
    def test_with_mock(self, mock_external):
        """使用 mock 的测试"""
        mock_external.return_value = "mocked_result"
        result = your_function_that_calls_external()
        self.assertEqual(result, "mocked_result")
        mock_external.assert_called_once()
```

## 📝 代码规范

### Python 代码风格

遵循 PEP 8 标准：

```python
# 导入顺序
import os
import sys
from pathlib import Path

import third_party_lib

from local_module import LocalClass

# 常量
MAX_FILE_SIZE = 1024 * 1024  # 1MB

# 类定义
class MyTool:
    """工具类文档字符串"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def process_file(self, file_path, output_dir=None):
        """
        处理单个文件
        
        Args:
            file_path (Path): 输入文件路径
            output_dir (Path, optional): 输出目录
            
        Returns:
            Path: 输出文件路径
            
        Raises:
            FileNotFoundError: 输入文件不存在
        """
        # 实现逻辑
        pass

# 函数定义
def helper_function(param1, param2=None):
    """辅助函数文档字符串"""
    if param2 is None:
        param2 = []
    
    return result
```

### 文档字符串规范

使用 Google 风格的文档字符串：

```python
def complex_function(param1, param2, param3=None):
    """
    函数的简短描述
    
    更详细的函数说明，如果需要的话。可以包含多行。
    
    Args:
        param1 (str): 第一个参数的描述
        param2 (int): 第二个参数的描述
        param3 (list, optional): 可选参数的描述. 默认为 None.
        
    Returns:
        bool: 返回值的描述
        
    Raises:
        ValueError: 参数无效时抛出
        FileNotFoundError: 文件不存在时抛出
        
    Example:
        >>> result = complex_function("hello", 42)
        >>> print(result)
        True
    """
    pass
```

### 错误处理

```python
def process_file(file_path):
    """处理文件，包含适当的错误处理"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 处理逻辑
        with file_path.open() as f:
            data = f.read()
        
        # 验证数据
        if not data.strip():
            raise ValueError("File is empty")
        
        return process_data(data)
        
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        raise
    except ValueError as e:
        print(f"Error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
```

## 🔧 配置管理

### pyproject.toml 配置

```toml
[project]
name = "toolkit"
version = "1.0.0"
description = "A collection of useful system utilities and tools"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "textual>=0.45.0",
    "pillow>=9.0.0"
]

[project.scripts]
toolkit = "main:main"
your-tool = "tools.your_tool.main:main"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0"
]

[tool.black]
line-length = 88
target-version = ["py38"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["tools"]
omit = ["tests/*", "*/test_*"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 环境配置

创建 `.env` 文件（不要提交到版本控制）：

```env
# 开发环境配置
DEBUG=true
LOG_LEVEL=debug
TEMP_DIR=/tmp/toolkit
```

## 📚 文档维护

### 文档类型

1. **README.md**: 用户使用指南
2. **ARCHITECTURE.md**: 架构设计文档
3. **DEVELOPMENT.md**: 开发指南（本文档）
4. **API 文档**: 代码自动生成的 API 文档

### 文档更新原则

- 代码变更时同步更新相关文档
- 新功能必须包含使用示例
- 保持文档的时效性和准确性

## 🚀 发布流程

### 版本管理

使用语义版本号（SemVer）：
- `MAJOR.MINOR.PATCH`
- 例如：`1.2.3`

### 发布步骤

1. **更新版本号**:
   ```bash
   # 编辑 pyproject.toml
   version = "1.1.0"
   ```

2. **更新变更日志**:
   编辑 `docs/CHANGELOG.md`

3. **运行完整测试**:
   ```bash
   python -m pytest tests/
   black --check .
   flake8 .
   ```

4. **提交变更**:
   ```bash
   git add .
   git commit -m "Release v1.1.0"
   git tag v1.1.0
   ```

5. **推送到远程**:
   ```bash
   git push origin main --tags
   ```

## 🐛 调试技巧

### 调试工具

```python
# 使用 pdb 调试
import pdb; pdb.set_trace()

# 使用 logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

### 性能分析

```python
# 时间性能分析
import time
import cProfile
import pstats

def profile_function():
    start_time = time.time()
    
    # 你的代码
    result = expensive_operation()
    
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    
    return result

# 使用 cProfile
cProfile.run('your_function()', 'profile_stats')
p = pstats.Stats('profile_stats')
p.sort_stats('cumulative').print_stats(10)
```

## 🤝 贡献流程

### Git 工作流

1. **克隆仓库**:
   ```bash
   git clone <repository-url>
   cd toolkit
   ```

2. **创建功能分支**:
   ```bash
   git checkout -b feature/new-tool
   ```

3. **开发和测试**:
   ```bash
   # 开发代码
   # 运行测试
   python -m pytest tests/
   ```

4. **提交变更**:
   ```bash
   git add .
   git commit -m "Add new tool for X functionality"
   ```

5. **推送分支**:
   ```bash
   git push origin feature/new-tool
   ```

6. **创建 Pull Request**

### Pull Request 指南

- 清晰的标题和描述
- 包含测试用例
- 更新相关文档
- 通过所有检查

### 代码审查

- 遵循代码规范
- 功能完整性
- 测试覆盖率
- 文档完整性
- 性能影响

## 💡 开发技巧

### IDE 配置

#### VS Code 配置

创建 `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "files.associations": {
        "*.md": "markdown"
    }
}
```

### 常用开发命令

```bash
# 开发环境设置
make setup          # 或自定义脚本

# 代码检查
make lint           # black + flake8 + mypy
make test           # 运行测试
make coverage       # 测试覆盖率

# 清理
make clean          # 清理临时文件

# 文档
make docs           # 生成文档
```

### 有用的脚本

创建 `scripts/dev.py`:

```python
#!/usr/bin/env python3
"""开发辅助脚本"""

import argparse
import subprocess
import sys

def run_tests():
    """运行测试"""
    return subprocess.run([sys.executable, "-m", "pytest", "tests/"])

def check_code():
    """检查代码"""
    commands = [
        [sys.executable, "-m", "black", "--check", "."],
        [sys.executable, "-m", "flake8", "."],
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            return result.returncode
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["test", "check", "format"])
    args = parser.parse_args()
    
    if args.command == "test":
        sys.exit(run_tests().returncode)
    elif args.command == "check":
        sys.exit(check_code())
    elif args.command == "format":
        subprocess.run([sys.executable, "-m", "black", "."])

if __name__ == "__main__":
    main()
```

---

这份开发指南会持续更新以反映最佳实践。如有问题或建议，请提交 Issue 或 Pull Request。