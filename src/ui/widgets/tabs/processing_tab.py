"""
文档处理 Tab
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QLabel,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Qt


class ProcessingTab(QWidget):
    """文档处理 Tab"""

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

        # 文本处理
        text_group = QLabel("文本处理")
        text_group.setObjectName("settings_group_title")
        layout.addWidget(text_group)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(16)

        self.split_short_lines = QCheckBox("分割短行")
        self.split_short_lines.setMinimumHeight(28)
        text_layout.addWidget(self.split_short_lines)

        layout.addLayout(text_layout)

        # 分割因子
        split_form = QFormLayout()
        split_form.setSpacing(12)

        self.short_line_split_factor = QSpinBox()
        self.short_line_split_factor.setRange(0, 100)
        self.short_line_split_factor.setSingleStep(1)
        self.short_line_split_factor.setValue(80)
        split_form.addRow("短行分割因子 (0-100):", self.short_line_split_factor)

        layout.addLayout(split_form)

        # 公式处理
        formula_group = QLabel("公式处理")
        formula_group.setObjectName("settings_group_title")
        layout.addWidget(formula_group)

        formula_layout = QVBoxLayout()
        formula_layout.setSpacing(16)

        self.skip_form_render = QCheckBox("跳过公式渲染")
        self.skip_form_render.setMinimumHeight(28)
        formula_layout.addWidget(self.skip_form_render)

        self.skip_curve_render = QCheckBox("跳过曲线渲染")
        self.skip_curve_render.setMinimumHeight(28)
        formula_layout.addWidget(self.skip_curve_render)

        layout.addLayout(formula_layout)

        # 高级选项
        advanced_group = QLabel("高级选项")
        advanced_group.setObjectName("settings_group_title")
        layout.addWidget(advanced_group)

        advanced_layout = QVBoxLayout()
        advanced_layout.setSpacing(16)

        self.only_parse_generate_pdf = QCheckBox("仅解析生成 PDF")
        self.only_parse_generate_pdf.setMinimumHeight(28)
        advanced_layout.addWidget(self.only_parse_generate_pdf)

        self.remove_non_formula_lines = QCheckBox("移除非公式行")
        self.remove_non_formula_lines.setMinimumHeight(28)
        advanced_layout.addWidget(self.remove_non_formula_lines)

        self.only_include_translated_page = QCheckBox("仅包含翻译页面")
        self.only_include_translated_page.setMinimumHeight(28)
        advanced_layout.addWidget(self.only_include_translated_page)

        self.merge_alternating_line_numbers = QCheckBox("合并交替行号")
        self.merge_alternating_line_numbers.setMinimumHeight(28)
        advanced_layout.addWidget(self.merge_alternating_line_numbers)

        layout.addLayout(advanced_layout)

        # 阈值设置
        threshold_form = QFormLayout()
        threshold_form.setSpacing(12)

        self.non_formula_line_iou_threshold = QSpinBox()
        self.non_formula_line_iou_threshold.setRange(0, 100)
        self.non_formula_line_iou_threshold.setSingleStep(1)
        self.non_formula_line_iou_threshold.setValue(90)
        threshold_form.addRow(
            "非公式行 IoU 阈值 (%):", self.non_formula_line_iou_threshold
        )

        self.figure_table_protection_threshold = QSpinBox()
        self.figure_table_protection_threshold.setRange(0, 100)
        self.figure_table_protection_threshold.setSingleStep(1)
        self.figure_table_protection_threshold.setValue(90)
        threshold_form.addRow(
            "图表保护阈值 (%):", self.figure_table_protection_threshold
        )

        layout.addLayout(threshold_form)

        # 字体设置
        font_group = QLabel("字体设置")
        font_group.setObjectName("settings_group_title")
        layout.addWidget(font_group)

        font_form = QFormLayout()
        font_form.setSpacing(12)

        self.primary_font_family = QComboBox()
        self.primary_font_family.addItems(
            ["无", "serif (衬线)", "sans-serif (无衬线)", "script (手写)"]
        )
        font_form.addRow("主要字体系列:", self.primary_font_family)

        layout.addLayout(font_form)

        layout.addStretch()

        # 将内容放入滚动区域
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def load_settings(self):
        """加载设置"""
        settings = self.settings_store.get_settings()
        pdf = settings.pdf

        # 设置复选框
        self.split_short_lines.setChecked(pdf.split_short_lines)
        self.skip_form_render.setChecked(pdf.skip_form_render)
        self.skip_curve_render.setChecked(pdf.skip_curve_render)
        self.only_parse_generate_pdf.setChecked(pdf.only_parse_generate_pdf)
        self.remove_non_formula_lines.setChecked(pdf.remove_non_formula_lines)
        self.only_include_translated_page.setChecked(pdf.only_include_translated_page)
        self.merge_alternating_line_numbers.setChecked(
            pdf.merge_alternating_line_numbers
        )

        # 设置数值（转换为整数百分比）
        self.short_line_split_factor.setValue(int(pdf.short_line_split_factor * 100))
        self.non_formula_line_iou_threshold.setValue(
            int(pdf.non_formula_line_iou_threshold * 100)
        )
        self.figure_table_protection_threshold.setValue(
            int(pdf.figure_table_protection_threshold * 100)
        )

        # 设置字体
        font_map = {
            None: "无",
            "serif": "serif (衬线)",
            "sans-serif": "sans-serif (无衬线)",
            "script": "script (手写)",
        }
        font_text = font_map.get(pdf.primary_font_family, "无")
        self.primary_font_family.setCurrentText(font_text)

    def save_settings(self):
        """保存设置"""
        font_reverse_map = {
            "无": None,
            "serif (衬线)": "serif",
            "sans-serif (无衬线)": "sans-serif",
            "script (手写)": "script",
        }

        self.settings_store.update_pdf_settings(
            split_short_lines=self.split_short_lines.isChecked(),
            short_line_split_factor=self.short_line_split_factor.value() / 100.0,
            skip_form_render=self.skip_form_render.isChecked(),
            skip_curve_render=self.skip_curve_render.isChecked(),
            only_parse_generate_pdf=self.only_parse_generate_pdf.isChecked(),
            remove_non_formula_lines=self.remove_non_formula_lines.isChecked(),
            only_include_translated_page=self.only_include_translated_page.isChecked(),
            merge_alternating_line_numbers=self.merge_alternating_line_numbers.isChecked(),
            non_formula_line_iou_threshold=self.non_formula_line_iou_threshold.value()
            / 100.0,
            figure_table_protection_threshold=self.figure_table_protection_threshold.value()
            / 100.0,
            primary_font_family=font_reverse_map.get(
                self.primary_font_family.currentText()
            ),
        )
