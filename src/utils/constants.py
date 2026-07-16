"""
共享常量定义
"""

# 语言映射 - 代码到显示名称
LANG_CODE_TO_DISPLAY = {
    "zh": "中文 (zh)",
    "en": "English (en)",
    "ja": "日本語 (ja)",
    "ko": "한국어 (ko)",
    "fr": "Français (fr)",
    "de": "Deutsch (de)",
    "es": "Español (es)",
    "pt": "Português (pt)",
    "ru": "Русский (ru)",
    "ar": "العربية (ar)",
    "it": "Italiano (it)",
}

# 语言映射 - 显示名称到代码
LANG_DISPLAY_TO_CODE = {v: k for k, v in LANG_CODE_TO_DISPLAY.items()}

# 水印模式映射
WATERMARK_CODE_TO_DISPLAY = {
    "watermarked": "watermarked (带水印)",
    "no_watermark": "no_watermark (无水印)",
    "both": "both (两者都输出)",
}

WATERMARK_DISPLAY_TO_CODE = {v: k for k, v in WATERMARK_CODE_TO_DISPLAY.items()}

# 字体映射
FONT_CODE_TO_DISPLAY = {
    None: "无",
    "serif": "serif (衬线)",
    "sans-serif": "sans-serif (无衬线)",
    "script": "script (手写)",
}

FONT_DISPLAY_TO_CODE = {v: k for k, v in FONT_CODE_TO_DISPLAY.items()}

# 服务商默认模型
PROVIDER_DEFAULT_MODELS = {
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "o1",
        "o1-mini",
        "o3-mini",
    ],
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
    "zhipu": ["glm-4-plus", "glm-4-flash", "glm-4-long", "glm-4"],
    "ollama": ["llama3.3", "llama3.2", "qwen2.5", "deepseek-r1", "phi4", "mistral"],
    "claude": [
        "claude-sonnet-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
    ],
}

# 服务商默认配置选项
PROVIDER_DEFAULT_OPTIONS = {
    "openai": {
        "enable_json_mode": False,
        "send_dashscope_header": False,
        "no_send_temperature": False,
    },
    "deepseek": {
        "enable_json_mode": False,
        "send_dashscope_header": False,
        "no_send_temperature": False,
    },
    "zhipu": {
        "enable_json_mode": False,
        "send_dashscope_header": True,
        "no_send_temperature": False,
    },
    "ollama": {
        "enable_json_mode": False,
        "send_dashscope_header": False,
        "no_send_temperature": False,
    },
    "claude": {
        "enable_json_mode": False,
        "send_dashscope_header": False,
        "no_send_temperature": True,
    },
}
