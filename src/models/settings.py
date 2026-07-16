"""
设置相关的数据模型
"""

from dataclasses import dataclass, field
from typing import Optional, List, Literal


# 常量定义
MAX_CUSTOM_PROMPT_LENGTH = 10000
MIN_QPS = 1
MAX_QPS = 100
MIN_WORKERS = 1
MAX_WORKERS = 50


@dataclass
class ModelConfig:
    """模型配置"""

    id: str
    display_name: str
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    enable_json_mode: bool = False
    send_dashscope_header: bool = False
    no_send_temperature: bool = False


@dataclass
class Provider:
    """服务商"""

    id: str
    name: str
    default_base_url: str
    is_builtin: bool = True
    icon: str = "auto_awesome"
    models: List[ModelConfig] = field(default_factory=list)


@dataclass
class ProviderSettings:
    """服务商设置"""

    providers: List[Provider] = field(default_factory=list)
    selected_model_id: str = ""


@dataclass
class TermExtractionSettings:
    """术语提取设置"""

    use_separate_config: bool = False
    model_config_id: str = ""
    custom_api_key: str = ""
    custom_base_url: str = ""
    custom_model: str = ""
    reasoning: str = ""


@dataclass
class TranslationSettings:
    """翻译设置"""

    lang_in: str = "en"
    lang_out: str = "zh"
    qps: int = 4
    min_text_length: int = 5
    pool_max_workers: Optional[int] = None
    term_pool_max_workers: Optional[int] = None
    custom_system_prompt: str = ""
    auto_extract_glossary: bool = True
    disable_same_text_fallback: bool = False
    add_formula_placehold_hint: bool = False
    ignore_cache: bool = False
    save_auto_extracted_glossary: bool = False

    def __post_init__(self):
        """参数验证"""
        # QPS 范围验证
        if self.qps < MIN_QPS:
            self.qps = MIN_QPS
        elif self.qps > MAX_QPS:
            self.qps = MAX_QPS

        # min_text_length 非负验证
        if self.min_text_length < 0:
            self.min_text_length = 0

        # pool_max_workers 范围验证
        if self.pool_max_workers is not None:
            if self.pool_max_workers < MIN_WORKERS:
                self.pool_max_workers = MIN_WORKERS
            elif self.pool_max_workers > MAX_WORKERS:
                self.pool_max_workers = MAX_WORKERS

        # term_pool_max_workers 范围验证
        if self.term_pool_max_workers is not None:
            if self.term_pool_max_workers < MIN_WORKERS:
                self.term_pool_max_workers = MIN_WORKERS
            elif self.term_pool_max_workers > MAX_WORKERS:
                self.term_pool_max_workers = MAX_WORKERS

        # custom_system_prompt 长度限制
        if len(self.custom_system_prompt) > MAX_CUSTOM_PROMPT_LENGTH:
            self.custom_system_prompt = self.custom_system_prompt[
                :MAX_CUSTOM_PROMPT_LENGTH
            ]


def _clamp_threshold(value: float) -> float:
    """将阈值限制在 [0.0, 1.0] 范围内"""
    return max(0.0, min(1.0, value))


@dataclass
class PDFSettings:
    """PDF 设置"""

    output_dual: bool = True
    output_mono: bool = True
    watermark_mode: Literal["watermarked", "no_watermark", "both"] = "watermarked"
    skip_clean: bool = False
    dual_translate_first: bool = False
    disable_rich_text_translate: bool = False
    enhance_compatibility: bool = False
    use_alternating_pages_dual: bool = False
    max_pages_per_part: Optional[int] = None
    skip_scanned_detection: bool = False
    ocr_workaround: bool = False
    auto_enable_ocr_workaround: bool = False
    split_short_lines: bool = False
    short_line_split_factor: float = 0.8
    primary_font_family: Optional[Literal["serif", "sans-serif", "script"]] = None
    formular_font_pattern: str = ""
    formular_char_pattern: str = ""
    skip_form_render: bool = False
    skip_curve_render: bool = False
    only_parse_generate_pdf: bool = False
    remove_non_formula_lines: bool = False
    non_formula_line_iou_threshold: float = 0.9
    figure_table_protection_threshold: float = 0.9
    translate_table_text: bool = False
    only_include_translated_page: bool = False
    merge_alternating_line_numbers: bool = False

    def __post_init__(self):
        """参数验证"""
        if not self.output_dual and not self.output_mono:
            self.output_dual = True

        # 阈值范围验证
        self.short_line_split_factor = _clamp_threshold(self.short_line_split_factor)
        self.non_formula_line_iou_threshold = _clamp_threshold(
            self.non_formula_line_iou_threshold
        )
        self.figure_table_protection_threshold = _clamp_threshold(
            self.figure_table_protection_threshold
        )

        # max_pages_per_part 正数验证
        if self.max_pages_per_part is not None and self.max_pages_per_part < 1:
            self.max_pages_per_part = None


@dataclass
class RPCSettings:
    """RPC 设置"""

    doclayout_host: str = ""


@dataclass
class PathSettings:
    """路径设置"""

    output_dir: str = ""
    working_dir: str = ""
    glossary_files: str = ""


@dataclass
class Settings:
    """完整设置"""

    providers: ProviderSettings = field(default_factory=ProviderSettings)
    term_extraction: TermExtractionSettings = field(
        default_factory=TermExtractionSettings
    )
    translation: TranslationSettings = field(default_factory=TranslationSettings)
    pdf: PDFSettings = field(default_factory=PDFSettings)
    rpc: RPCSettings = field(default_factory=RPCSettings)
    paths: PathSettings = field(default_factory=PathSettings)


# 内置服务商预设
BUILTIN_PROVIDERS = [
    {
        "id": "openai",
        "name": "OpenAI",
        "default_base_url": "https://api.openai.com/v1",
        "is_builtin": True,
        "icon": "auto_awesome",
    },
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "default_base_url": "https://api.deepseek.com",
        "is_builtin": True,
        "icon": "explore",
    },
    {
        "id": "zhipu",
        "name": "智谱 GLM",
        "default_base_url": "https://open.bigmodel.cn/api/paas/v4",
        "is_builtin": True,
        "icon": "psychology",
    },
    {
        "id": "ollama",
        "name": "Ollama (本地)",
        "default_base_url": "http://localhost:11434/v1",
        "is_builtin": True,
        "icon": "computer",
    },
    {
        "id": "claude",
        "name": "Claude (Anthropic)",
        "default_base_url": "https://api.anthropic.com/v1",
        "is_builtin": True,
        "icon": "chat",
    },
]


def create_default_settings() -> Settings:
    """创建默认设置"""
    default_providers = [Provider(**p) for p in BUILTIN_PROVIDERS]

    return Settings(
        providers=ProviderSettings(
            providers=default_providers,
            selected_model_id="",
        ),
        term_extraction=TermExtractionSettings(),
        translation=TranslationSettings(),
        pdf=PDFSettings(),
        rpc=RPCSettings(),
        paths=PathSettings(),
    )
