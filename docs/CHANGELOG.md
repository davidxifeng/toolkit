# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-08

### 🎉 项目重构为模块化工具箱架构

这是一个重大的架构重构版本，将原本单一的截图整理工具扩展为一个多工具集合的工具箱。

### Added
- **模块化架构**: 采用插件式架构设计，支持多个独立工具
- **统一主入口**: 新的 `main.py` 提供工具选择菜单和统一调用接口
- **多种调用方式**: 
  - 交互式菜单模式 (`python main.py`)
  - 直接工具调用 (`python main.py <tool> <args>`)
  - 独立脚本调用 (`./scripts/<tool-name>`)
  - 全局安装后调用 (`pip install -e .`)
- **图片重组工具**: 新增图片工具模块
  - 将水平拼接的图片转换为2D网格布局
  - 智能布局计算（最佳长宽比）
  - 支持自定义缩放和输出路径
  - 完整的类结构和CLI接口
- **独立可执行脚本**: 在 `scripts/` 目录下提供独立脚本
  - `scripts/toolkit` - 主工具选择器
  - `scripts/screenshot-org` - 截图整理工具
  - `scripts/image-reorg` - 图片重组工具
- **完善的测试框架**: 
  - 为每个工具模块添加单元测试
  - 集成测试覆盖
  - 测试示例和模板
- **项目文档系统**:
  - 全新的 README.md 用户指南
  - `docs/ARCHITECTURE.md` 架构设计文档
  - `docs/DEVELOPMENT.md` 开发者指南
  - 详细的添加新工具指南
- **标准化配置**: 
  - 更新 `pyproject.toml` 包含完整项目配置
  - 定义了脚本入口点
  - 添加开发依赖配置

### Changed
- **代码结构重组**:
  - `screenshot_organizer.py` → `tools/screenshot/organizer.py`
  - `screenshot_tui.py` → `tools/screenshot/tui.py`
  - `image_reorganizer.py` → `tools/image/reorganizer.py` (重构为类结构)
- **工具类重构**: 
  - 所有工具都采用类结构设计
  - 统一的参数验证和错误处理
  - 更好的模块化和可测试性
- **用户体验优化**:
  - 友好的交互式菜单界面
  - 统一的命令行参数风格
  - 改进的帮助信息和使用示例

### Technical Improvements
- **架构模式**:
  - 插件模式：每个工具是独立插件
  - 工厂模式：主入口根据选择创建工具实例
  - 命令模式：封装用户操作为命令对象
- **扩展机制**:
  - 清晰的工具注册流程
  - 标准化的工具接口规范
  - 支持多种界面类型（CLI、TUI等）
- **开发工具**:
  - 完整的测试体系
  - 代码格式化和检查配置
  - 详细的开发和贡献指南

### Documentation
- **用户文档**: 全面的使用指南，包含所有调用方式
- **开发文档**: 详细的架构说明和开发指南
- **代码示例**: 每个功能都有完整的使用示例
- **API文档**: 清晰的类和方法文档字符串

### Breaking Changes
- **入口点变更**: 原来的直接调用方式需要通过新的主入口
- **导入路径变更**: 内部模块路径发生改变（但用户接口保持兼容）

### Migration Guide
对于现有用户：

```bash
# 原来的调用方式
python screenshot_organizer.py --help

# 新的调用方式
python main.py screenshot --help
# 或使用脚本
./scripts/screenshot-org --help
# 或安装后全局调用
pip install -e . && screenshot-org --help
```

### Future Roadmap
- 添加更多实用工具模块
- Web界面支持
- 配置文件系统
- 插件市场机制
- 工具链和工作流支持

---

## [0.1.0] - 2024-XX-XX (历史版本)

### Added
- 初始的截图整理工具
- TUI 交互界面
- CLI 命令行界面
- 基本的文件组织功能

### Features
- macOS 截图文件识别
- 按日期和周次自动分类
- 支持预览和复制模式
- 递归目录扫描

---

## 版本说明

- **[Major.Minor.Patch]** 格式遵循语义版本控制
- **Major**: 不兼容的API变更
- **Minor**: 向后兼容的功能性新增
- **Patch**: 向后兼容的问题修正

## 标签说明

- 🎉 **重大更新**
- ✨ **新功能**
- 🐛 **Bug修复**
- 📚 **文档更新**
- ⚡ **性能优化**
- 🔧 **配置变更**
- 🚨 **破坏性变更**
- 🗑️ **废弃功能**