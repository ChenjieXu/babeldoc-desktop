"""翻译服务封装"""

import asyncio
from typing import AsyncIterator

import babeldoc.format.pdf.high_level as high_level
from babeldoc.format.pdf.translation_config import TranslationConfig, WatermarkOutputMode
from babeldoc.translator.translator import OpenAITranslator, set_translate_rate_limiter
from babeldoc.docvision.doclayout import DocLayoutModel


class TranslationService:
    """翻译服务封装"""

    def __init__(self):
        self.doc_layout_model = None
        self._initialized = False

    async def initialize(self):
        """初始化模型"""
        if self._initialized:
            return

        import sys

        def log(msg: str):
            print(f"[SIDECAR] {msg}", file=sys.stderr, flush=True)

        try:
            log("步骤 1/3: 初始化缓存目录...")
            high_level.init()
            log("步骤 1/3: 缓存目录初始化完成")

            log("步骤 2/3: 准备加载ONNX模型...")
            # 使用线程池异步加载模型，避免阻塞事件循环
            loop = asyncio.get_event_loop()
            self.doc_layout_model = await loop.run_in_executor(
                None,  # 使用默认线程池
                DocLayoutModel.load_onnx
            )
            log("步骤 2/3: ONNX模型加载完成")

            log("步骤 3/3: 初始化完成")
            self._initialized = True
        except Exception as e:
            log(f"初始化失败: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise

    async def translate(self, config_dict: dict) -> AsyncIterator[dict]:
        """执行翻译并流式返回进度"""
        if not self._initialized:
            await self.initialize()

        # 构建翻译器
        translator = OpenAITranslator(
            lang_in=config_dict["lang_in"],
            lang_out=config_dict["lang_out"],
            model=config_dict["model"],
            base_url=config_dict.get("base_url"),
            api_key=config_dict["api_key"],
            ignore_cache=config_dict.get("ignore_cache", False),
            enable_json_mode_if_requested=config_dict.get("enable_json_mode", False),
            send_dashscope_header=config_dict.get("send_dashscope_header", False),
            send_temperature=not config_dict.get("no_send_temperature", False),
        )

        # 设置 QPS 限制
        qps = config_dict.get("qps", 4)
        set_translate_rate_limiter(qps)

        # 水印模式映射
        watermark_map = {
            "watermarked": WatermarkOutputMode.Watermarked,
            "no_watermark": WatermarkOutputMode.NoWatermark,
            "both": WatermarkOutputMode.Both,
        }
        watermark_mode = watermark_map.get(
            config_dict.get("watermark_mode", "watermarked"),
            WatermarkOutputMode.Watermarked,
        )

        # 构建翻译配置
        config = TranslationConfig(
            input_file=config_dict["input_file"],
            translator=translator,
            doc_layout_model=self.doc_layout_model,
            lang_in=config_dict["lang_in"],
            lang_out=config_dict["lang_out"],
            pages=config_dict.get("pages"),
            output_dir=config_dict.get("output_dir"),
            no_dual=not config_dict.get("output_dual", True),
            no_mono=not config_dict.get("output_mono", True),
            watermark_output_mode=watermark_mode,
            skip_clean=config_dict.get("skip_clean", False),
            enhance_compatibility=config_dict.get("enhance_compatibility", False),
            disable_rich_text_translate=config_dict.get("disable_rich_text_translate", False),
        )

        # 执行异步翻译
        async for event in high_level.async_translate(config):
            # 转换事件格式
            if event["type"] == "progress_update":
                yield {
                    "type": "progress_update",
                    "stage": event.get("stage", ""),
                    "stageCurrent": event.get("stage_current", 0),
                    "stageTotal": event.get("stage_total", 0),
                    "overallProgress": event.get("overall_progress", 0),
                }
            elif event["type"] == "error":
                # 确保错误可序列化
                error_val = event.get("error", "Unknown error")
                yield {
                    "type": "error",
                    "error": str(error_val),
                }
            elif event["type"] == "finish":
                result = event.get("translate_result", {})
                yield {
                    "type": "finish",
                    "translateResult": {
                        "originalPdfPath": str(result.original_pdf_path) if hasattr(result, "original_pdf_path") else "",
                        "totalSeconds": getattr(result, "total_seconds", 0),
                        "monoPdfPath": str(result.mono_pdf_path) if hasattr(result, "mono_pdf_path") and result.mono_pdf_path else None,
                        "dualPdfPath": str(result.dual_pdf_path) if hasattr(result, "dual_pdf_path") and result.dual_pdf_path else None,
                        "noWatermarkMonoPdfPath": str(result.no_watermark_mono_pdf_path) if hasattr(result, "no_watermark_mono_pdf_path") and result.no_watermark_mono_pdf_path else None,
                        "noWatermarkDualPdfPath": str(result.no_watermark_dual_pdf_path) if hasattr(result, "no_watermark_dual_pdf_path") and result.no_watermark_dual_pdf_path else None,
                    },
                }
