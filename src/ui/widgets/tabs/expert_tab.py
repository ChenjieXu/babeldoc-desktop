"""
专家选项 Tab
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QSpinBox,
    QLabel,
    QScrollArea,
    QFrame,
)


class ExpertTab(QWidget):
    """专家选项 Tab"""

    def __init__(self, settings_store):
        super().__init__()
        self.settings_store = settings_store
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 警告信息
        warning_label = QLabel(
            "[!] 这些选项仅建议高级用户使用，修改不当可能导致翻译失败或结果异常。"
        )
        warning_label.setObjectName("warning_card")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 0, 20, 0)
        content_layout.setSpacing(24)

        # --- 公式识别 ---
        formula_group = self._create_group("公式识别", content_layout)
        self.formular_font_pattern = self._add_field(
            "公式字体模式:", "例如: Times New Roman", formula_group
        )
        self.formular_char_pattern = self._add_field(
            "公式字符模式:", "例如: αβγδεζηθικλμνξοπρστυφχψω", formula_group
        )

        # --- 工作线程数 ---
        workers_group = self._create_group("工作线程数", content_layout)

        # 翻译线程
        self.pool_max_workers = QSpinBox()
        self.pool_max_workers.setRange(0, 50)
        self.pool_max_workers.setValue(0)
        self.pool_max_workers.setSpecialValueText("自动")
        self._add_field_widget("翻译线程池大小:", self.pool_max_workers, workers_group)

        # 术语线程
        self.term_pool_max_workers = QSpinBox()
        self.term_pool_max_workers.setRange(0, 20)
        self.term_pool_max_workers.setValue(0)
        self.term_pool_max_workers.setSpecialValueText("自动")
        self._add_field_widget(
            "术语提取线程池大小:", self.term_pool_max_workers, workers_group
        )

        # --- RPC 设置 ---
        rpc_group = self._create_group("RPC 设置", content_layout)
        self.doclayout_host = self._add_field(
            "文档布局服务地址:", "例如: http://localhost:8080", rpc_group
        )

        # --- 路径设置 ---
        path_group = self._create_group("路径设置", content_layout)
        self.output_dir = self._add_field(
            "输出目录:", "留空时保存到原 PDF 所在文件夹", path_group
        )
        self.working_dir = self._add_field("工作目录:", "留空使用默认位置", path_group)
        self.glossary_files = self._add_field(
            "术语表 CSV:", "多个文件用英文逗号分隔", path_group
        )

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # 说明
        info_label = QLabel("[提示] 输出目录留空时，翻译结果保存在原 PDF 所在文件夹。")
        info_label.setObjectName("subtitle")
        layout.addWidget(info_label)

    def _create_group(self, title: str, parent_layout: QVBoxLayout) -> QVBoxLayout:
        """创建分组"""
        group_label = QLabel(title)
        group_label.setObjectName("settings_group_title")
        parent_layout.addWidget(group_label)

        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)
        parent_layout.addLayout(group_layout)

        # Add spacing after group
        parent_layout.addSpacing(8)

        return group_layout

    def _add_field(
        self, label_text: str, placeholder: str, parent_layout: QVBoxLayout
    ) -> QLineEdit:
        """添加文本字段"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel(label_text)
        label.setObjectName("field_label")
        layout.addWidget(label)

        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        layout.addWidget(input_field)

        parent_layout.addWidget(container)
        return input_field

    def _add_field_widget(
        self, label_text: str, widget: QWidget, parent_layout: QVBoxLayout
    ):
        """添加自定义控件字段"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel(label_text)
        label.setObjectName("field_label")
        layout.addWidget(label)

        layout.addWidget(widget)
        parent_layout.addWidget(container)

    def load_settings(self):
        """加载设置"""
        settings = self.settings_store.get_settings()

        # 公式
        pdf = settings.pdf
        self.formular_font_pattern.setText(pdf.formular_font_pattern or "")
        self.formular_char_pattern.setText(pdf.formular_char_pattern or "")

        # 线程数
        trans = settings.translation
        if trans.pool_max_workers:
            self.pool_max_workers.setValue(trans.pool_max_workers)
        else:
            self.pool_max_workers.setValue(0)

        if trans.term_pool_max_workers:
            self.term_pool_max_workers.setValue(trans.term_pool_max_workers)
        else:
            self.term_pool_max_workers.setValue(0)

        # RPC
        rpc = settings.rpc
        self.doclayout_host.setText(rpc.doclayout_host or "")

        # 路径
        paths = settings.paths
        self.output_dir.setText(paths.output_dir or "")
        self.working_dir.setText(paths.working_dir or "")
        self.glossary_files.setText(paths.glossary_files or "")

    def save_settings(self):
        """保存设置"""
        self.settings_store.update_translation_settings(
            pool_max_workers=self.pool_max_workers.value()
            if self.pool_max_workers.value() > 0
            else None,
            term_pool_max_workers=self.term_pool_max_workers.value()
            if self.term_pool_max_workers.value() > 0
            else None,
        )

        self.settings_store.update_pdf_settings(
            formular_font_pattern=self.formular_font_pattern.text().strip(),
            formular_char_pattern=self.formular_char_pattern.text().strip(),
        )

        self.settings_store.update_rpc_settings(
            doclayout_host=self.doclayout_host.text().strip()
        )

        self.settings_store.update_path_settings(
            output_dir=self.output_dir.text().strip(),
            working_dir=self.working_dir.text().strip(),
            glossary_files=self.glossary_files.text().strip(),
        )
