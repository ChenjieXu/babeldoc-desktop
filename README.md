# BabelDOC Desktop

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tauri](https://img.shields.io/badge/Tauri-2.0+-blue)](https://tauri.app/)
[![Vue](https://img.shields.io/badge/Vue-3.0+-green)](https://vuejs.org/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)

基于 Tauri + Vue 3 + Python 的 BabelDOC 桌面应用，支持 PDF 文档智能翻译。

## ✨ 功能特性

- 🚀 **高性能桌面应用**：基于 Tauri 构建，原生性能体验
- 📄 **智能 PDF 翻译**：支持多种 PDF 格式的智能翻译
- 🌍 **多语言支持**：支持中英文等多语言翻译
- 🤖 **多模型集成**：集成 OpenAI、DeepSeek、智谱、Ollama、Claude 等主流 AI 模型
- 📝 **灵活输出**：支持双语/单语 PDF 输出
- 📊 **实时进度**：翻译进度实时显示
- ⚙️ **设置持久化**：用户设置自动保存
- 🎨 **现代化 UI**：基于 Vue 3 + TypeScript 的美观界面

## 🚀 快速开始

### 系统要求

- **Node.js**: 20.0+
- **Rust**: 1.70+ (通过 [rustup](https://rustup.rs/) 安装)
- **Python**: 3.12+
- **操作系统**: Windows 10+ / macOS 10.15+ / Ubuntu 18.04+

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/babeldoc-desktop.git
   cd babeldoc-desktop
   ```

2. **安装前端依赖**
   ```bash
   npm install
   ```

3. **安装 Python 后端依赖**
   ```bash
   cd python-backend
   pip install -r requirements.txt
   cd ..
   ```

4. **启动开发模式**
   ```bash
   npm run tauri dev
   ```

## 🏗️ 项目结构

这是一个 **Monorepo** 项目，包含多个子项目：

```
babeldoc-desktop/
├── src/                    # Vue 3 前端源码
│   ├── components/         # UI 组件
│   ├── stores/             # Pinia 状态管理
│   ├── types/              # TypeScript 类型定义
│   ├── services/           # API 服务封装
│   └── assets/             # 静态资源
├── src-tauri/              # Tauri Rust 后端
│   ├── src/                # Rust 源码
│   ├── binaries/           # Python sidecar 二进制
│   └── icons/              # 应用图标
├── python-backend/         # Python 后端服务
│   ├── main.py             # 主服务入口
│   ├── server.py           # HTTP 服务器
│   └── requirements.txt    # Python 依赖
├── BabelDOC/               # BabelDOC Python 核心库
│   ├── babeldoc/           # 核心源码
│   ├── docs/               # 文档
│   └── pyproject.toml      # 项目配置
├── scripts/                # 构建和工具脚本
│   ├── build-python.sh     # Python 构建脚本
│   ├── create_icons.py     # 图标生成脚本
│   └── test_app.py         # 测试脚本
├── docs/                   # 项目文档
│   ├── CLAUDE.md           # AI 助手指南
│   └── TEST_REPORT.md      # 测试报告
└── examples/               # 示例文件
```

## 🛠️ 开发指南

### 开发环境设置

```bash
# 安装所有依赖
npm install

# Python 环境
cd python-backend && pip install -r requirements.txt && cd ..

# 启动开发服务器
npm run tauri dev
```

### 构建应用

```bash
# 构建 Python sidecar
./scripts/build-python.sh

# 构建桌面应用
npm run tauri build
```

### 发布新版本

项目使用 GitHub Actions 自动构建和发布：

1. **创建标签**：推送版本标签触发自动构建
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **自动构建**：GitHub Actions 会自动在以下平台构建：
   - macOS (Intel + Apple Silicon)
   - Windows
   - Linux (Ubuntu)

3. **自动发布**：构建完成后自动创建 GitHub Release 并上传安装包

支持的安装包格式：
- **macOS**: `.dmg`, `.pkg`
- **Windows**: `.msi`, `.exe`
- **Linux**: `.deb`, `.rpm`, `.AppImage`

### 代码规范

- **前端**: 使用 ESLint + Prettier
- **后端**: 遵循 PEP 8 规范
- **Rust**: 使用 rustfmt + clippy

### 测试

```bash
# 运行前端测试
npm test

# 运行 Python 测试
cd BabelDOC && python -m pytest && cd ..
```

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

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Tauri](https://tauri.app/) - 现代桌面应用框架
- [Vue.js](https://vuejs.org/) - 渐进式前端框架
- [BabelDOC](https://github.com/funstory-ai/BabelDOC) - PDF 翻译核心库
- [Vite](https://vitejs.dev/) - 快速构建工具

## 📞 联系方式

- 项目主页: [GitHub](https://github.com/your-username/babeldoc-desktop)
- 问题反馈: [Issues](https://github.com/your-username/babeldoc-desktop/issues)
- 邮箱: your-email@example.com

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！
