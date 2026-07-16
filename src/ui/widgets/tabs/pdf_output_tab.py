"""
PDF 输出 Tab
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QLabel,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Qt


class PDFOutputTab(QWidget):
    """PDF 输出 Tab"""

    def __init__(self, settings_store):
        super().__init__()
        self.settings_store = settings_store
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """设置 UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: #ffffff; border: none; }")

        # 内容容器
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 输出格式
        format_group = QLabel("输出格式")
        format_group.setObjectName("settings_group_title")
        layout.addWidget(format_group)

        format_layout = QVBoxLayout()
        format_layout.setSpacing(12)

        self.output_dual = QCheckBox("输出双语 PDF")
        format_layout.addWidget(self.output_dual)

        self.output_mono = QCheckBox("输出单语 PDF")
        format_layout.addWidget(self.output_mono)

        self.output_dual.toggled.connect(self._ensure_output_selected)
        self.output_mono.toggled.connect(self._ensure_output_selected)

        layout.addLayout(format_layout)

        # 水印设置
        watermark_group = QLabel("水印设置")
        watermark_group.setObjectName("settings_group_title")
        layout.addWidget(watermark_group)

        watermark_form = QFormLayout()
        watermark_form.setSpacing(12)

        self.watermark_mode = QComboBox()
        self.watermark_mode.addItems(
            ["watermarked (带水印)", "no_watermark (无水印)", "both (两者都输出)"]
        )
        watermark_form.addRow("水印模式:", self.watermark_mode)

        layout.addLayout(watermark_form)

        # 处理选项
        processing_group = QLabel("处理选项")
        processing_group.setObjectName("settings_group_title")
        layout.addWidget(processing_group)

        processing_layout = QVBoxLayout()
        processing_layout.setSpacing(12)

        self.skip_clean = QCheckBox("跳过清理")
        processing_layout.addWidget(self.skip_clean)

        self.enhance_compatibility = QCheckBox("增强兼容性")
        processing_layout.addWidget(self.enhance_compatibility)

        self.dual_translate_first = QCheckBox("双语翻译优先")
        processing_layout.addWidget(self.dual_translate_first)

        self.disable_rich_text_translate = QCheckBox("禁用富文本翻译")
        processing_layout.addWidget(self.disable_rich_text_translate)

        layout.addLayout(processing_layout)

        # 高级选项
        advanced_group = QLabel("高级选项")
        advanced_group.setObjectName("settings_group_title")
        layout.addWidget(advanced_group)

        advanced_form = QFormLayout()
        advanced_form.setSpacing(12)

        self.max_pages_per_part = QSpinBox()
        self.max_pages_per_part.setRange(0, 1000)
        self.max_pages_per_part.setValue(0)
        self.max_pages_per_part.setSpecialValueText("无限制")
        advanced_form.addRow("每部分最大页数:", self.max_pages_per_part)

        layout.addLayout(advanced_form)

        # 其他选项
        other_layout = QVBoxLayout()
        other_layout.setSpacing(12)

        self.use_alternating_pages_dual = QCheckBox("使用交替页面双语")
        other_layout.addWidget(self.use_alternating_pages_dual)

        self.skip_scanned_detection = QCheckBox("跳过扫描检测")
        other_layout.addWidget(self.skip_scanned_detection)

        self.ocr_workaround = QCheckBox("OCR 变通方法")
        other_layout.addWidget(self.ocr_workaround)

        self.auto_enable_ocr_workaround = QCheckBox("自动启用 OCR 变通")
        other_layout.addWidget(self.auto_enable_ocr_workaround)

        layout.addLayout(other_layout)

        layout.addStretch()

        # 将内容放入滚动区域
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _ensure_output_selected(self, _checked: bool) -> None:
        """Prevent the UI from accepting a paid translation with no PDF output."""
        if self.output_dual.isChecked() or self.output_mono.isChecked():
            return
        other = (
            self.output_mono if self.sender() is self.output_dual else self.output_dual
        )
        other.setChecked(True)

    def load_settings(self):
        """加载设置"""
        settings = self.settings_store.get_settings()
        pdf = settings.pdf

        # 设置复选框
        self.output_dual.setChecked(pdf.output_dual)
        self.output_mono.setChecked(pdf.output_mono)
        self.skip_clean.setChecked(pdf.skip_clean)
        self.enhance_compatibility.setChecked(pdf.enhance_compatibility)
        self.dual_translate_first.setChecked(pdf.dual_translate_first)
        self.disable_rich_text_translate.setChecked(pdf.disable_rich_text_translate)
        self.use_alternating_pages_dual.setChecked(pdf.use_alternating_pages_dual)
        self.skip_scanned_detection.setChecked(pdf.skip_scanned_detection)
        self.ocr_workaround.setChecked(pdf.ocr_workaround)
        self.auto_enable_ocr_workaround.setChecked(pdf.auto_enable_ocr_workaround)

        # 设置水印模式
        watermark_map = {
            "watermarked": "watermarked (带水印)",
            "no_watermark": "no_watermark (无水印)",
            "both": "both (两者都输出)",
        }
        watermark_text = watermark_map.get(pdf.watermark_mode, "watermarked (带水印)")
        self.watermark_mode.setCurrentText(watermark_text)

        # 设置最大页数
        if pdf.max_pages_per_part:
            self.max_pages_per_part.setValue(pdf.max_pages_per_part)
        else:
            self.max_pages_per_part.setValue(0)

    def save_settings(self):
        """保存设置"""
        watermark_reverse_map = {
            "watermarked (带水印)": "watermarked",
            "no_watermark (无水印)": "no_watermark",
            "both (两者都输出)": "both",
        }

        self.settings_store.update_pdf_settings(
            output_dual=self.output_dual.isChecked(),
            output_mono=self.output_mono.isChecked(),
            watermark_mode=watermark_reverse_map.get(
                self.watermark_mode.currentText(), "watermarked"
            ),
            skip_clean=self.skip_clean.isChecked(),
            enhance_compatibility=self.enhance_compatibility.isChecked(),
            dual_translate_first=self.dual_translate_first.isChecked(),
            disable_rich_text_translate=self.disable_rich_text_translate.isChecked(),
            use_alternating_pages_dual=self.use_alternating_pages_dual.isChecked(),
            max_pages_per_part=self.max_pages_per_part.value()
            if self.max_pages_per_part.value() > 0
            else None,
            skip_scanned_detection=self.skip_scanned_detection.isChecked(),
            ocr_workaround=self.ocr_workaround.isChecked(),
            auto_enable_ocr_workaround=self.auto_enable_ocr_workaround.isChecked(),
        )
