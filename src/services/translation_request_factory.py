"""Build typed translation requests from persisted settings and runtime overrides."""

from pathlib import Path
from typing import Optional

from src.models.settings import ModelConfig, Settings
from src.models.translation import RuntimeOverrides, TranslationConfig, UploadedFile


def build_translation_request(
    *,
    settings: Settings,
    model: ModelConfig,
    file: UploadedFile,
    runtime: RuntimeOverrides,
    term_model: Optional[ModelConfig] = None,
) -> TranslationConfig:
    """Map settings and typed UI overrides to the complete BabelDOC contract."""
    trans = settings.translation
    pdf = settings.pdf
    paths = settings.paths
    term = settings.term_extraction
    output_dir = (
        Path(paths.output_dir).expanduser()
        if paths.output_dir.strip()
        else Path(file.path).expanduser().absolute().parent
    )

    return TranslationConfig(
        input_file=file.path,
        lang_in=runtime.lang_in,
        lang_out=runtime.lang_out,
        pages=runtime.pages,
        qps=runtime.qps,
        model=model.model_name,
        api_key=model.api_key,
        base_url=model.base_url,
        output_dir=str(output_dir),
        working_dir=paths.working_dir or None,
        glossary_files=(
            runtime.glossary_files
            if runtime.glossary_files is not None
            else paths.glossary_files or None
        ),
        output_dual=(
            runtime.output_dual if runtime.output_dual is not None else pdf.output_dual
        ),
        output_mono=(
            runtime.output_mono if runtime.output_mono is not None else pdf.output_mono
        ),
        watermark_mode=pdf.watermark_mode,
        enhance_compatibility=pdf.enhance_compatibility,
        skip_clean=pdf.skip_clean,
        ignore_cache=trans.ignore_cache,
        enable_json_mode=model.enable_json_mode,
        send_dashscope_header=model.send_dashscope_header,
        no_send_temperature=model.no_send_temperature,
        min_text_length=trans.min_text_length,
        pool_max_workers=trans.pool_max_workers,
        term_pool_max_workers=trans.term_pool_max_workers,
        custom_system_prompt=trans.custom_system_prompt,
        auto_extract_glossary=(
            runtime.auto_extract_glossary
            if runtime.auto_extract_glossary is not None
            else trans.auto_extract_glossary
        ),
        save_auto_extracted_glossary=trans.save_auto_extracted_glossary,
        add_formula_placehold_hint=trans.add_formula_placehold_hint,
        dual_translate_first=(
            runtime.dual_translate_first
            if runtime.dual_translate_first is not None
            else pdf.dual_translate_first
        ),
        disable_rich_text_translate=pdf.disable_rich_text_translate,
        use_alternating_pages_dual=(
            runtime.use_alternating_pages_dual
            if runtime.use_alternating_pages_dual is not None
            else pdf.use_alternating_pages_dual
        ),
        max_pages_per_part=pdf.max_pages_per_part,
        skip_scanned_detection=pdf.skip_scanned_detection,
        ocr_workaround=pdf.ocr_workaround,
        auto_enable_ocr_workaround=pdf.auto_enable_ocr_workaround,
        split_short_lines=pdf.split_short_lines,
        short_line_split_factor=pdf.short_line_split_factor,
        primary_font_family=pdf.primary_font_family,
        formular_font_pattern=pdf.formular_font_pattern or None,
        formular_char_pattern=pdf.formular_char_pattern or None,
        skip_form_render=pdf.skip_form_render,
        skip_curve_render=pdf.skip_curve_render,
        only_parse_generate_pdf=pdf.only_parse_generate_pdf,
        remove_non_formula_lines=pdf.remove_non_formula_lines,
        non_formula_line_iou_threshold=pdf.non_formula_line_iou_threshold,
        figure_table_protection_threshold=pdf.figure_table_protection_threshold,
        only_include_translated_page=pdf.only_include_translated_page,
        merge_alternating_line_numbers=pdf.merge_alternating_line_numbers,
        doclayout_host=settings.rpc.doclayout_host or None,
        term_extraction_use_separate_config=term.use_separate_config,
        term_extraction_model=(
            term_model.model_name if term_model else term.custom_model or None
        ),
        term_extraction_api_key=(
            term_model.api_key if term_model else term.custom_api_key or None
        ),
        term_extraction_base_url=(
            term_model.base_url if term_model else term.custom_base_url or None
        ),
        term_extraction_reasoning=term.reasoning or None,
    )
