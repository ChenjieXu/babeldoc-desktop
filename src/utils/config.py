"""
配置管理工具
"""

import json
import os
import logging
import tempfile
import types
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any, Literal, Optional, Union, get_args, get_origin
from dataclasses import fields

from src.models.settings import Settings, create_default_settings

logger = logging.getLogger(__name__)


def _restrict_permissions(path: Path, mode: int) -> None:
    """Best-effort POSIX permission hardening for settings and secrets."""
    if os.name != "posix":
        return
    try:
        path.chmod(mode)
    except OSError as exc:
        logger.warning("无法收紧配置权限 %s: %s", path, exc)


# 字段名映射：dataclass字段 -> JSON字段
FIELD_MAPPINGS = {
    "default_base_url": "defaultBaseUrl",
    "is_builtin": "isBuiltin",
    "display_name": "displayName",
    "model_name": "modelName",
    "api_key": "apiKey",
    "base_url": "baseUrl",
    "enable_json_mode": "enableJsonMode",
    "send_dashscope_header": "sendDashscopeHeader",
    "no_send_temperature": "noSendTemperature",
    "use_separate_config": "useSeparateConfig",
    "model_config_id": "modelConfigId",
    "custom_api_key": "customApiKey",
    "custom_base_url": "customBaseUrl",
    "custom_model": "customModel",
    "lang_in": "langIn",
    "lang_out": "langOut",
    "min_text_length": "minTextLength",
    "pool_max_workers": "poolMaxWorkers",
    "term_pool_max_workers": "termPoolMaxWorkers",
    "custom_system_prompt": "customSystemPrompt",
    "auto_extract_glossary": "autoExtractGlossary",
    "disable_same_text_fallback": "disableSameTextFallback",
    "add_formula_placehold_hint": "addFormulaPlaceholdHint",
    "ignore_cache": "ignoreCache",
    "save_auto_extracted_glossary": "saveAutoExtractedGlossary",
    "output_dual": "outputDual",
    "output_mono": "outputMono",
    "watermark_mode": "watermarkMode",
    "skip_clean": "skipClean",
    "dual_translate_first": "dualTranslateFirst",
    "disable_rich_text_translate": "disableRichTextTranslate",
    "enhance_compatibility": "enhanceCompatibility",
    "use_alternating_pages_dual": "useAlternatingPagesDual",
    "max_pages_per_part": "maxPagesPerPart",
    "skip_scanned_detection": "skipScannedDetection",
    "ocr_workaround": "ocrWorkaround",
    "auto_enable_ocr_workaround": "autoEnableOcrWorkaround",
    "split_short_lines": "splitShortLines",
    "short_line_split_factor": "shortLineSplitFactor",
    "primary_font_family": "primaryFontFamily",
    "formular_font_pattern": "formularFontPattern",
    "formular_char_pattern": "formularCharPattern",
    "skip_form_render": "skipFormRender",
    "skip_curve_render": "skipCurveRender",
    "only_parse_generate_pdf": "onlyParseGeneratePdf",
    "remove_non_formula_lines": "removeNonFormulaLines",
    "non_formula_line_iou_threshold": "nonFormulaLineIouThreshold",
    "figure_table_protection_threshold": "figureTableProtectionThreshold",
    "translate_table_text": "translateTableText",
    "only_include_translated_page": "onlyIncludeTranslatedPage",
    "merge_alternating_line_numbers": "mergeAlternatingLineNumbers",
    "doclayout_host": "doclayoutHost",
    "output_dir": "outputDir",
    "working_dir": "workingDir",
    "glossary_files": "glossaryFiles",
    "selected_model_id": "selectedModelId",
}

# 反向映射
REVERSE_MAPPINGS = {v: k for k, v in FIELD_MAPPINGS.items()}


def _to_camel_case(key: str) -> str:
    """将snake_case转换为camelCase"""
    return FIELD_MAPPINGS.get(
        key,
        "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(key.split("_"))
        ),
    )


def _to_snake_case(key: str) -> str:
    """将camelCase转换为snake_case"""
    return REVERSE_MAPPINGS.get(
        key, "".join("_" + c.lower() if c.isupper() else c for c in key).lstrip("_")
    )


def _convert_dict_keys(data: Dict[str, Any], converter) -> Dict[str, Any]:
    """递归转换字典的键"""
    result = {}
    for key, value in data.items():
        new_key = converter(key)
        if isinstance(value, dict):
            result[new_key] = _convert_dict_keys(value, converter)
        elif isinstance(value, list):
            result[new_key] = [
                _convert_dict_keys(item, converter) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[new_key] = value
    return result


def get_config_dir() -> Path:
    """获取配置目录"""
    if os.name == "nt":
        appdata = os.environ.get("APPDATA", "")
        if appdata and Path(appdata).is_absolute():
            config_dir = Path(appdata) / "babeldoc-desktop"
        else:
            config_dir = Path.home() / "AppData" / "Roaming" / "babeldoc-desktop"
    elif os.name == "posix":
        config_dir = Path.home() / ".config" / "babeldoc-desktop"
    else:
        config_dir = Path.home() / ".babeldoc-desktop"

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        logger.error(f"无法创建配置目录: {e}")
        config_dir = Path.home() / ".babeldoc-desktop"
        config_dir.mkdir(parents=True, exist_ok=True)

    _restrict_permissions(config_dir, 0o700)

    return config_dir


def get_settings_path() -> Path:
    """获取设置文件路径"""
    return get_config_dir() / "settings.json"


def load_settings() -> Dict[str, Any]:
    """加载设置"""
    settings_path = get_settings_path()
    if settings_path.exists():
        _restrict_permissions(settings_path, 0o600)
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误，将使用默认设置: {e}")
            backup_path = settings_path.with_suffix(".json.bak")
            try:
                settings_path.rename(backup_path)
                logger.info(f"已备份损坏的配置文件到: {backup_path}")
            except OSError:
                pass
        except (PermissionError, OSError) as e:
            logger.error(f"无法读取配置文件: {e}")
    return settings_to_dict(create_default_settings())


def save_settings(settings: Dict[str, Any]):
    """保存设置（原子写入）"""
    settings_path = get_settings_path()
    config_dir = settings_path.parent
    temp_path: Optional[Path] = None

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        _restrict_permissions(config_dir, 0o700)

        fd, temp_name = tempfile.mkstemp(
            dir=config_dir,
            prefix=f".{settings_path.name}.",
            suffix=".tmp",
        )
        temp_path = Path(temp_name)
        if os.name == "posix":
            os.fchmod(fd, 0o600)

        with os.fdopen(fd, "w", encoding="utf-8") as file_handle:
            json.dump(settings, file_handle, indent=2, ensure_ascii=False)
            file_handle.flush()
            os.fsync(file_handle.fileno())

        os.replace(temp_path, settings_path)
        temp_path = None
        _restrict_permissions(settings_path, 0o600)
    except Exception:
        logger.exception("保存配置文件失败: %s", settings_path)
        raise
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def settings_to_dict(settings: Settings) -> Dict[str, Any]:
    """将 Settings 对象转换为字典（使用映射后的字段名）"""

    def convert(obj) -> Dict[str, Any]:
        """递归转换dataclass为字典，应用字段名映射"""
        if not hasattr(obj, "__dataclass_fields__"):
            return obj
        result = {}
        for field in fields(obj):
            value = getattr(obj, field.name)
            json_key = _to_camel_case(field.name)
            if isinstance(value, list):
                result[json_key] = [
                    convert(item) if hasattr(item, "__dataclass_fields__") else item
                    for item in value
                ]
            elif hasattr(value, "__dataclass_fields__"):
                result[json_key] = convert(value)
            else:
                result[json_key] = value
        return result

    return convert(settings)


def dict_to_settings(data: Dict[str, Any]) -> Settings:
    """Recover a valid Settings object from current, legacy, or partial JSON."""
    from src.models.settings import (
        Settings,
        ProviderSettings,
        Provider,
        ModelConfig,
        TermExtractionSettings,
        TranslationSettings,
        PDFSettings,
        RPCSettings,
        PathSettings,
    )

    defaults = create_default_settings()
    if not isinstance(data, dict):
        logger.warning("配置根节点不是对象，已恢复默认设置")
        return defaults

    def as_mapping(value: Any, section: str) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value
        if value is not None:
            logger.warning("忽略类型错误的配置段: %s", section)
        return {}

    def value_matches(value: Any, annotation: Any) -> bool:
        if annotation is Any:
            return True
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Literal:
            return value in args
        if origin in (Union, types.UnionType):
            return any(value_matches(value, option) for option in args)
        if origin is list:
            return isinstance(value, list) and (
                not args or all(value_matches(item, args[0]) for item in value)
            )
        if annotation is float:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if annotation is int:
            return isinstance(value, int) and not isinstance(value, bool)
        if isinstance(annotation, type):
            return isinstance(value, annotation)
        return True

    def build_section(obj_class, raw: Any, default_obj, section: str):
        raw_mapping = as_mapping(raw, section)
        values = {
            field.name: deepcopy(getattr(default_obj, field.name))
            for field in fields(obj_class)
        }
        for field in fields(obj_class):
            json_key = _to_camel_case(field.name)
            if json_key in raw_mapping:
                candidate = raw_mapping[json_key]
            elif field.name in raw_mapping:
                candidate = raw_mapping[field.name]
            else:
                continue
            if candidate is None and isinstance(values[field.name], str):
                # Older UI versions serialized empty path/pattern fields as null.
                candidate = ""
            if value_matches(candidate, field.type):
                values[field.name] = candidate
            else:
                logger.warning("忽略类型错误的配置字段: %s.%s", section, json_key)
        return obj_class(**values)

    providers_data = as_mapping(data.get("providers"), "providers")
    raw_providers = providers_data.get("providers")
    default_by_id = {
        provider.id: deepcopy(provider) for provider in defaults.providers.providers
    }
    parsed_by_id: Dict[str, Provider] = {}
    custom_order: list[str] = []

    if isinstance(raw_providers, list):
        for index, raw_provider in enumerate(raw_providers):
            if not isinstance(raw_provider, dict):
                logger.warning("忽略无效服务商配置: providers[%s]", index)
                continue
            provider_id = raw_provider.get("id")
            if not isinstance(provider_id, str) or not provider_id:
                logger.warning("忽略缺少 id 的服务商配置: providers[%s]", index)
                continue

            base = default_by_id.get(provider_id)
            name = raw_provider.get("name", base.name if base else None)
            default_url = raw_provider.get(
                "defaultBaseUrl",
                raw_provider.get(
                    "default_base_url", base.default_base_url if base else None
                ),
            )
            if not isinstance(name, str) or not isinstance(default_url, str):
                logger.warning("忽略缺少名称或 URL 的服务商: %s", provider_id)
                continue

            raw_models = raw_provider.get("models", [])
            models = []
            if isinstance(raw_models, list):
                for model_index, raw_model in enumerate(raw_models):
                    if not isinstance(raw_model, dict):
                        logger.warning(
                            "忽略无效模型配置: %s.models[%s]",
                            provider_id,
                            model_index,
                        )
                        continue
                    model_id = raw_model.get("id")
                    model_name = raw_model.get("modelName", raw_model.get("model_name"))
                    if not isinstance(model_id, str) or not isinstance(model_name, str):
                        logger.warning(
                            "忽略缺少 id 或 modelName 的模型: %s.models[%s]",
                            provider_id,
                            model_index,
                        )
                        continue
                    model_defaults = ModelConfig(
                        id=model_id,
                        display_name=model_name,
                        model_name=model_name,
                        api_key="",
                        base_url=default_url,
                    )
                    models.append(
                        build_section(
                            ModelConfig,
                            raw_model,
                            model_defaults,
                            f"providers.{provider_id}.models[{model_index}]",
                        )
                    )
            else:
                logger.warning("忽略类型错误的模型列表: %s.models", provider_id)

            provider = Provider(
                id=provider_id,
                name=name,
                default_base_url=default_url,
                is_builtin=(
                    raw_provider.get("isBuiltin", base.is_builtin if base else False)
                    if isinstance(
                        raw_provider.get(
                            "isBuiltin", base.is_builtin if base else False
                        ),
                        bool,
                    )
                    else (base.is_builtin if base else False)
                ),
                icon=(
                    raw_provider.get("icon")
                    if isinstance(raw_provider.get("icon"), str)
                    else (base.icon if base else "auto_awesome")
                ),
                models=models,
            )
            parsed_by_id[provider_id] = provider
            if provider_id not in default_by_id:
                custom_order.append(provider_id)
    elif raw_providers is not None:
        logger.warning("忽略类型错误的服务商列表")

    providers = [
        parsed_by_id.get(provider.id, provider)
        for provider in defaults.providers.providers
    ]
    providers.extend(parsed_by_id[provider_id] for provider_id in custom_order)
    model_ids = {model.id for provider in providers for model in provider.models}
    selected_model_id = providers_data.get(
        "selectedModelId", providers_data.get("selected_model_id", "")
    )
    if not isinstance(selected_model_id, str) or selected_model_id not in model_ids:
        selected_model_id = ""
    provider_settings = ProviderSettings(providers, selected_model_id)

    term_settings = build_section(
        TermExtractionSettings,
        data.get("termExtraction"),
        defaults.term_extraction,
        "termExtraction",
    )
    translation_settings = build_section(
        TranslationSettings,
        data.get("translation"),
        defaults.translation,
        "translation",
    )
    pdf_settings = build_section(PDFSettings, data.get("pdf"), defaults.pdf, "pdf")
    rpc_settings = build_section(RPCSettings, data.get("rpc"), defaults.rpc, "rpc")
    path_settings = build_section(
        PathSettings, data.get("paths"), defaults.paths, "paths"
    )

    return Settings(
        providers=provider_settings,
        term_extraction=term_settings,
        translation=translation_settings,
        pdf=pdf_settings,
        rpc=rpc_settings,
        paths=path_settings,
    )
