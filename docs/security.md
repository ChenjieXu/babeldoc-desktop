# 安全与隐私

## API Key 存储

BabelDOC Desktop 将模型设置保存在当前用户的 `settings.json` 中，目前不使用系统钥匙串。

- Windows：`%APPDATA%/babeldoc-desktop/settings.json`
- macOS / Linux：`~/.config/babeldoc-desktop/settings.json`

在 POSIX 系统中，应用会尝试将设置目录和文件权限分别收紧为 `0700` 和 `0600`。

## 使用建议

- 使用仅具备必要权限的 API Key；
- 不要把配置文件、日志或主目录备份公开分享；
- 截图设置页面前确认 API Key 已隐藏；
- 通过企业代理或自定义 Base URL 时，确认服务端的日志与数据保留政策；
- 使用 Ollama 等本地服务时，确认监听地址没有暴露到不可信网络。

## 文档内容

PDF 内容会被发送到你选择的翻译服务或本地模型。BabelDOC Desktop 本身不提供云端账户，但第三方模型服务可能记录请求；请遵循相应服务条款和组织的数据处理政策。

## 报告安全问题

不要在公开 Issue 中粘贴 API Key、完整配置或包含敏感文档内容的日志。请先通过仓库维护者可用的私密渠道联系，并提供最小化的复现信息。
