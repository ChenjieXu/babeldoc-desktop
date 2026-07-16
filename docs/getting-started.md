# 快速开始

## 下载桌面版本

前往 [GitHub Releases](https://github.com/ChenjieXu/babeldoc-desktop/releases/latest)，根据系统下载对应文件：

| 系统 | 架构 | 文件后缀 |
| --- | --- | --- |
| macOS | Apple Silicon | `macos-arm64.zip` |
| macOS | Intel | `macos-x64.zip` |
| Windows | x64 | `windows-x64.zip` |
| Linux | x64 | `linux-x64.tar.gz` |

下载后可使用 Release 中的 `SHA256SUMS.txt` 校验文件完整性。

!!! warning "首次启动提示"
    当前构建未进行商业代码签名。macOS 或 Windows 可能要求你确认应用来源；请只从本仓库的正式 Release 下载。

## 从源码运行

需要 Python 3.10 或更高版本，并建议使用 [uv](https://docs.astral.sh/uv/) 管理环境。

```bash
git clone https://github.com/ChenjieXu/babeldoc-desktop.git
cd babeldoc-desktop
uv sync --frozen --extra dev
uv run --frozen --extra dev python run.py
```

## 第一次配置

1. 打开右上角 **设置**。
2. 在 **模型与服务** 中选择服务商并添加模型。
3. 填写模型名称、API Key 和 Base URL。
4. 保存设置并返回主工作台。
5. 添加 PDF，确认本次任务选项，然后开始翻译。

API Key 的存储方式和保护建议见[安全与隐私](security.md)。
