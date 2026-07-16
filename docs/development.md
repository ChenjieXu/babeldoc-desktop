# 开发指南

## 环境准备

```bash
uv sync --frozen --extra dev
```

## 运行应用

```bash
uv run --frozen --extra dev python run.py
```

## 质量检查

```bash
uv run --frozen ruff check .
QT_QPA_PLATFORM=offscreen \
  uv run --frozen python -m unittest discover -s tests -p "test_*.py" -v
uv run --frozen python -m compileall -q src tests hooks
uv pip check
```

## 打包

```bash
uv run --frozen --extra dev python build.py
```

默认使用 PyInstaller。Nuitka 为可选路径：

```bash
uv run --with nuitka python build.py --nuitka
```

## 架构

```text
UI → Stores → Services → Models
```

- `src/ui/`：PySide6 窗口、组件和 QSS；
- `src/stores/`：Qt 信号驱动的应用状态；
- `src/services/`：设置、请求构建和翻译编排；
- `src/models/`：设置与翻译数据模型；
- `src/utils/`：配置持久化、资源路径与文件工具。

## 文档站

本地构建 Read the Docs 使用的 MkDocs 站点：

```bash
uv run \
  --with mkdocs==1.6.1 \
  --with mkdocs-material==9.7.6 \
  mkdocs build --strict
```

维护者发布检查清单见[维护者发布](RELEASING.md)。
