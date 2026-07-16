"""
翻译相关的数据模型
"""

from dataclasses import dataclass
from typing import Optional, Literal
from enum import Enum


class EventType(Enum):
    """事件类型"""

    PROGRESS_UPDATE = "progress_update"
    FINISH = "finish"
    ERROR = "error"
    LOG = "log"


@dataclass(frozen=True)
class ProgressUpdateEvent:
    """进度更新事件（不可变）"""

    type: Literal["progress_update"] = "progress_update"
    stage: str = ""
    stage_current: int = 0
    stage_total: int = 0
    overall_progress: int = 0


@dataclass(frozen=True)
class TranslateResult:
    """翻译结果（不可变）"""

    original_pdf_path: str
    total_seconds: float
    mono_pdf_path: Optional[str] = None
    dual_pdf_path: Optional[str] = None
    no_watermark_mono_pdf_path: Optional[str] = None
    no_watermark_dual_pdf_path: Optional[str] = None
    peak_memory_usage: Optional[float] = None
    auto_extracted_glossary_path: Optional[str] = None


@dataclass(frozen=True)
class FinishEvent:
    """完成事件（不可变）"""

    type: Literal["finish"] = "finish"
    translate_result: Optional[TranslateResult] = None


@dataclass(frozen=True)
class ErrorEvent:
    """错误事件（不可变）"""

    type: Literal["error"] = "error"
    error: str = ""


@dataclass(frozen=True)
class LogEvent:
    """日志事件（不可变）"""

    type: Literal["log"] = "log"
    message: str = ""


# 联合事件类型
TranslationEvent = ProgressUpdateEvent | FinishEvent | ErrorEvent | LogEvent


@dataclass(frozen=True)
class UploadedFile:
    """上传的文件（不可变）"""

    id: str
    name: str
    path: str
    size: int


@dataclass(frozen=True)
class RuntimeOverrides:
    """Validated main-window values that override persisted translation defaults."""

    lang_in: str
    lang_out: str
    pages: Optional[str]
    qps: int
    output_dual: Optional[bool] = None
    output_mono: Optional[bool] = None
    use_alternating_pages_dual: Optional[bool] = None
    dual_translate_first: Optional[bool] = None
    auto_extract_glossary: Optional[bool] = None
    glossary_files: Optional[str] = None


@dataclass(frozen=True)
class ResultFile:
    """结果文件（不可变）"""

    name: str
    path: str
    file_type: Literal[
        "单语 PDF", "双语 PDF", "无水印单语 PDF", "无水印双语 PDF", "术语表 CSV"
    ]


@dataclass
class TranslationConfig:
    """完整的单次翻译请求。"""

    input_file: str
    lang_in: str
    lang_out: str
    model: str
    api_key: str
    base_url: Optional[str] = None
    pages: Optional[str] = None
    output_dir: Optional[str] = None
    working_dir: Optional[str] = None
    glossary_files: Optional[str] = None
    output_dual: bool = True
    output_mono: bool = True
    watermark_mode: Optional[str] = "watermarked"
    enhance_compatibility: bool = False
    skip_clean: bool = False
    qps: int = 4
    min_text_length: int = 5
    pool_max_workers: Optional[int] = None
    term_pool_max_workers: Optional[int] = None
    custom_system_prompt: str = ""
    auto_extract_glossary: bool = False
    save_auto_extracted_glossary: bool = False
    add_formula_placehold_hint: bool = False
    ignore_cache: bool = False
    enable_json_mode: bool = False
    send_dashscope_header: bool = False
    no_send_temperature: bool = False
    dual_translate_first: bool = False
    disable_rich_text_translate: bool = False
    use_alternating_pages_dual: bool = False
    max_pages_per_part: Optional[int] = None
    skip_scanned_detection: bool = False
    ocr_workaround: bool = False
    auto_enable_ocr_workaround: bool = False
    split_short_lines: bool = False
    short_line_split_factor: float = 0.8
    primary_font_family: Optional[Literal["serif", "sans-serif", "script"]] = None
    formular_font_pattern: Optional[str] = None
    formular_char_pattern: Optional[str] = None
    skip_form_render: bool = False
    skip_curve_render: bool = False
    only_parse_generate_pdf: bool = False
    remove_non_formula_lines: bool = False
    non_formula_line_iou_threshold: float = 0.9
    figure_table_protection_threshold: float = 0.9
    only_include_translated_page: bool = False
    merge_alternating_line_numbers: bool = False
    doclayout_host: Optional[str] = None
    term_extraction_use_separate_config: bool = False
    term_extraction_model: Optional[str] = None
    term_extraction_api_key: Optional[str] = None
    term_extraction_base_url: Optional[str] = None
    term_extraction_reasoning: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.output_dual and not self.output_mono:
            raise ValueError("至少需要启用一种 PDF 输出格式")
