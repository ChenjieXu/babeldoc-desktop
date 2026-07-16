# BabelDOC Desktop

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Qt](https://img.shields.io/badge/Qt-PySide6-green)](https://doc.qt.io/qtforpython/)

基于 Python + PySide6 (Qt) 的 BabelDOC 桌面应用，支持 PDF 文档智能翻译。

## ✨ 功能特性

- 🚀 **原生桌面体验**：基于 PySide6 构建，流畅稳定的桌面体验
- 📄 **智能 PDF 翻译**：集成 BabelDOC 核心，支持高质量文档翻译
- 🌍 **多语言支持**：支持中英文等多语言互译
- 🤖 **多模型集成**：支持 OpenAI、DeepSeek、智谱、Ollama 等主流 AI 模型
- ⚙️ **可视化配置**：简洁直观的设置界面
- 📊 **实时进度**：翻译任务进度实时监控

## 🚀 快速开始

### 系统要求

- **Python**: 3.10+
- **操作系统**: Windows 10+ / macOS 10.15+ / Ubuntu 20.04+

### 安装步骤

1. **安装 uv** (Python 包管理器)
   ```bash
   # macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **克隆项目**

   ```bash
   git clone <repository-url>
   cd babeldoc-desktop
   ```

3. **同步环境与依赖**
   使用 uv 自动创建虚拟环境并安装依赖：
   ```bash
   uv sync --frozen --extra dev
   ```

4. **启动应用**
   ```bash
   uv run --frozen --extra dev python run.py
   ```

## 🏗️ 项目结构

```
babeldoc-desktop/
├── src/                    # 源代码
│   ├── ui/                 # PySide6 界面代码
│   ├── services/           # 业务逻辑服务
│   ├── models/             # 数据模型
│   ├── stores/             # 状态管理
│   ├── utils/              # 工具函数
│   └── app.py              # 应用入口配置
├── resources/              # 应用图标等静态资源
├── tests/                  # unittest 测试
├── run.py                  # 启动脚本
├── build.py                # PyInstaller / Nuitka 打包入口
├── pyproject.toml          # 项目与打包配置
├── uv.lock                 # uv 锁定环境
└── requirements.txt        # 项目依赖
```

## 📦 打包应用

先按上文安装 `dev` extra，再使用项目打包脚本：

```bash
# PyInstaller（默认）
uv run --frozen --extra dev python build.py

# Nuitka（可选，Nuitka 不在项目锁定环境中）
uv run --with nuitka python build.py --nuitka
```

构建结果位于 `dist/`。

## 🛠️ 开发指南

### 代码规范

- **Python**: 遵循 PEP 8 规范

### 测试

```bash
# 运行 Python 测试
uv run --frozen python -m unittest discover -s tests -p "test_*.py" -v

# 构建 wheel
uv build --wheel --out-dir wheelhouse --clear
```

## 🔐 安全说明

API 密钥保存在当前用户的 `settings.json` 中，而不是由系统钥匙串托管。POSIX 系统会将设置文件和目录权限分别收紧为 `0600` 和 `0700`；仍应保护好用户账户、配置目录和备份。

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发约定

- 使用 [Conventional Commits](https://conventionalcommits.org/) 格式
- 为新功能编写测试
- 更新相关文档
- 确保所有测试通过

## 📄 许可证

本项目采用 AGPL-3.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python
- [BabelDOC](https://github.com/funstory-ai/BabelDOC) - PDF 翻译核心库

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！
