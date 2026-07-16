"""
服务商管理 Tab
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QFormLayout,
    QComboBox,
    QCheckBox,
    QMessageBox,
)
from PySide6.QtCore import Qt
from src.models.settings import ModelConfig
from src.utils.constants import PROVIDER_DEFAULT_MODELS, PROVIDER_DEFAULT_OPTIONS
from uuid import uuid4


class ProviderTab(QWidget):
    """服务商管理 Tab"""

    def __init__(self, settings_store):
        super().__init__()
        self.settings_store = settings_store
        self.current_provider = None
        self.setup_ui()
        self.load_providers()

    def setup_ui(self):
        """设置 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 左侧：服务商列表
        left_panel = self._create_left_panel()
        layout.addWidget(left_panel, 1)

        # 右侧：模型配置
        right_panel = self._create_right_panel()
        layout.addWidget(right_panel, 2)

    def _create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 标题
        title = QLabel("服务商列表")
        title.setObjectName("h2")
        layout.addWidget(title)

        # 服务商列表
        self.provider_list = QListWidget()
        self.provider_list.itemClicked.connect(self._on_provider_selected)
        layout.addWidget(self.provider_list)

        # 添加模型按钮
        self.add_model_button = QPushButton("添加模型")
        self.add_model_button.setObjectName("primary")
        self.add_model_button.clicked.connect(self._on_add_model)
        layout.addWidget(self.add_model_button)

        return panel

    def _create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # 标题
        title = QLabel("模型配置")
        title.setObjectName("h2")
        layout.addWidget(title)

        # 表单
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # 模型名称
        self.model_name_input = QComboBox()
        self.model_name_input.addItems(
            ["gpt-3.5-turbo", "gpt-4", "新模型"]
        )  # 添加常用模型
        form_layout.addRow("模型名称:", self.model_name_input)

        # 显示名称
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("例如: GPT-4")
        form_layout.addRow("显示名称:", self.display_name_input)

        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入 API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("API Key:", self.api_key_input)

        # Base URL
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("例如: https://api.openai.com/v1")
        form_layout.addRow("Base URL:", self.base_url_input)

        # 选项
        options_layout = QVBoxLayout()

        self.enable_json_mode = QCheckBox("启用 JSON 模式")
        options_layout.addWidget(self.enable_json_mode)

        self.send_dashscope_header = QCheckBox("发送 Dashscope Header")
        options_layout.addWidget(self.send_dashscope_header)

        self.no_send_temperature = QCheckBox("不发送温度参数")
        options_layout.addWidget(self.no_send_temperature)

        form_layout.addRow("选项:", options_layout)

        layout.addLayout(form_layout)

        layout.addStretch()

        # 按钮栏
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("success")
        self.save_button.clicked.connect(self._on_save_model)
        buttons_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("删除")
        self.delete_button.setObjectName("error")
        self.delete_button.clicked.connect(self._on_delete_model)
        buttons_layout.addWidget(self.delete_button)

        layout.addLayout(buttons_layout)

        return panel

    def load_providers(self):
        """加载服务商列表"""
        self.provider_list.clear()

        providers = self.settings_store.get_providers()
        for provider in providers:
            provider_item = QListWidgetItem(provider.name)
            provider_item.setData(Qt.UserRole, provider)
            self.provider_list.addItem(provider_item)

            # 添加该服务商的模型
            for model in provider.models:
                model_item = QListWidgetItem(f"  └ {model.display_name}")
                model_item.setData(Qt.UserRole, (provider, model))
                model_item.setData(Qt.UserRole + 1, "model")
                self.provider_list.addItem(model_item)

    def _on_provider_selected(self, item: QListWidgetItem):
        """服务商选中"""
        data = item.data(Qt.UserRole)

        # 安全检查：确保 data 是有效类型
        if data is None:
            return

        # Qt 会将 tuple 转换为 list，所以这里用 list 判断
        if isinstance(data, (tuple, list)) and len(data) == 2:  # 模型
            provider, model = data
            # 类型检查
            if not hasattr(provider, "id") or not hasattr(model, "id"):
                return
            self.current_provider = provider
            self._update_model_options()  # 更新模型下拉框选项
            self._load_model_config(model)
        elif hasattr(data, "id") and hasattr(
            data, "name"
        ):  # 服务商 - 检查是否有 id 和 name 属性
            self.current_provider = data
            self._update_model_options()  # 更新模型下拉框选项
            # 查找该服务商的第一个模型并选中
            current_index = self.provider_list.row(item)
            for i in range(current_index + 1, self.provider_list.count()):
                next_item = self.provider_list.item(i)
                next_data = next_item.data(Qt.UserRole)
                if (
                    isinstance(next_data, (tuple, list)) and len(next_data) == 2
                ):  # 找到模型
                    self.provider_list.setCurrentItem(next_item)
                    _, model = next_data
                    self._load_model_config(model)
                    return
                elif hasattr(next_data, "id"):  # 遇到下一个服务商，停止
                    break
            # 没有模型则应用默认配置并提示
            self._apply_default_config()
            QMessageBox.information(
                self,
                "提示",
                f'服务商 "{data.name}" 下没有模型，请点击「添加模型」创建一个。',
            )

    def _update_model_options(self):
        """根据当前服务商更新模型下拉框选项"""
        if not self.current_provider or not hasattr(self.current_provider, "id"):
            return

        # 获取当前服务商对应的默认模型列表
        provider_id = self.current_provider.id
        default_models = PROVIDER_DEFAULT_MODELS.get(provider_id, ["custom-model"])

        # 更新模型名称下拉框
        self.model_name_input.clear()
        self.model_name_input.addItems(default_models)
        self.model_name_input.setEditable(True)  # 允许用户输入自定义模型名

        # 更新 base_url
        self.base_url_input.setText(self.current_provider.default_base_url)

    def _apply_default_config(self):
        """应用当前服务商的默认配置"""
        if not self.current_provider:
            self._clear_model_config()
            return

        provider_id = self.current_provider.id
        default_options = PROVIDER_DEFAULT_OPTIONS.get(provider_id, {})
        default_models = PROVIDER_DEFAULT_MODELS.get(provider_id, ["custom-model"])

        if default_models:
            self.model_name_input.setCurrentText(default_models[0])

        self.display_name_input.clear()
        self.api_key_input.clear()
        self.base_url_input.setText(self.current_provider.default_base_url)
        self.enable_json_mode.setChecked(default_options.get("enable_json_mode", False))
        self.send_dashscope_header.setChecked(
            default_options.get("send_dashscope_header", False)
        )
        self.no_send_temperature.setChecked(
            default_options.get("no_send_temperature", False)
        )

    def _set_model_config(
        self,
        model_name: str,
        display_name: str,
        api_key: str,
        enable_json: bool,
        send_header: bool,
        no_temp: bool,
    ):
        """设置模型配置"""
        self.model_name_input.setCurrentText(model_name)
        self.display_name_input.setText(display_name)
        self.api_key_input.setText(api_key)
        self.enable_json_mode.setChecked(enable_json)
        self.send_dashscope_header.setChecked(send_header)
        self.no_send_temperature.setChecked(no_temp)

    def _load_model_config(self, model: ModelConfig):
        """加载模型配置"""
        if not model or not hasattr(model, "model_name"):
            return
        if not self.current_provider or not hasattr(
            self.current_provider, "default_base_url"
        ):
            return

        self._set_model_config(
            model.model_name,
            model.display_name,
            model.api_key,
            model.enable_json_mode,
            model.send_dashscope_header,
            model.no_send_temperature,
        )
        self.base_url_input.setText(
            model.base_url or self.current_provider.default_base_url
        )

    def _clear_model_config(self):
        """清空模型配置"""
        self._set_model_config("", "", "", False, False, False)
        self.base_url_input.clear()

    def _on_add_model(self):
        """添加模型"""
        if not self.current_provider:
            QMessageBox.warning(self, "提示", "请先选择一个服务商")
            return

        # 获取当前服务商的默认配置
        provider_id = self.current_provider.id
        default_options = PROVIDER_DEFAULT_OPTIONS.get(provider_id, {})
        default_models = PROVIDER_DEFAULT_MODELS.get(provider_id, ["custom-model"])
        default_model_name = default_models[0] if default_models else ""

        # 创建新模型（使用服务商的默认配置）
        model = ModelConfig(
            id=str(uuid4()),
            display_name="新模型",
            model_name=default_model_name,
            api_key="",
            base_url=self.current_provider.default_base_url,
            enable_json_mode=default_options.get("enable_json_mode", False),
            send_dashscope_header=default_options.get("send_dashscope_header", False),
            no_send_temperature=default_options.get("no_send_temperature", False),
        )

        # 添加到服务商
        if self.settings_store.add_model(self.current_provider.id, model):
            self.load_providers()
            # 选中新创建的模型并加载配置
            for i in range(self.provider_list.count()):
                item = self.provider_list.item(i)
                data = item.data(Qt.UserRole)
                if isinstance(data, (tuple, list)):
                    p, m = data
                    if m.id == model.id:
                        self.current_provider = p  # 更新 current_provider
                        self.provider_list.setCurrentItem(item)
                        self._update_model_options()
                        self._load_model_config(m)
                        break

    def _on_save_model(self):
        """保存模型"""
        if not self.current_provider:
            QMessageBox.warning(self, "提示", "请先选择一个服务商")
            return

        # 获取当前选中的模型
        current_item = self.provider_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择一个模型或服务商")
            return

        data = current_item.data(Qt.UserRole)

        # 如果选中的是服务商（不是模型），则创建新模型
        if not isinstance(data, (tuple, list)):
            self._create_and_save_new_model()
            return

        provider, model = data

        # 创建新的 ModelConfig 对象，避免修改旧引用
        updated_model = ModelConfig(
            id=model.id,
            display_name=self.display_name_input.text(),
            model_name=self.model_name_input.currentText(),
            api_key=self.api_key_input.text(),
            base_url=(self.base_url_input.text().strip() or provider.default_base_url),
            enable_json_mode=self.enable_json_mode.isChecked(),
            send_dashscope_header=self.send_dashscope_header.isChecked(),
            no_send_temperature=self.no_send_temperature.isChecked(),
        )

        # 保存
        if self.settings_store.update_model(provider.id, model.id, updated_model):
            self.load_providers()
            QMessageBox.information(self, "成功", "模型配置已保存")
            # 选中该模型并加载配置
            for i in range(self.provider_list.count()):
                item = self.provider_list.item(i)
                d = item.data(Qt.UserRole)
                if isinstance(d, (tuple, list)):
                    p, m = d
                    if m.id == model.id:
                        self.current_provider = p  # 更新 current_provider
                        self.provider_list.setCurrentItem(item)
                        self._update_model_options()
                        self._load_model_config(m)
                        break
        else:
            QMessageBox.warning(self, "失败", "保存模型配置失败")

    def _create_and_save_new_model(self):
        """创建并保存新模型"""
        if not self.current_provider:
            return

        # 获取表单中的配置
        model_name = self.model_name_input.currentText()
        display_name = self.display_name_input.text()

        if not display_name:
            display_name = model_name if model_name else "新模型"

        # 创建新模型
        model = ModelConfig(
            id=str(uuid4()),
            display_name=display_name,
            model_name=model_name,
            api_key=self.api_key_input.text(),
            base_url=(
                self.base_url_input.text().strip()
                or self.current_provider.default_base_url
            ),
            enable_json_mode=self.enable_json_mode.isChecked(),
            send_dashscope_header=self.send_dashscope_header.isChecked(),
            no_send_temperature=self.no_send_temperature.isChecked(),
        )

        # 添加到服务商
        if self.settings_store.add_model(self.current_provider.id, model):
            self.load_providers()
            QMessageBox.information(self, "成功", "模型配置已保存")
            # 选中新创建的模型并加载配置
            for i in range(self.provider_list.count()):
                item = self.provider_list.item(i)
                data = item.data(Qt.UserRole)
                if isinstance(data, (tuple, list)):
                    p, m = data
                    if m.id == model.id:
                        self.current_provider = p
                        self.provider_list.setCurrentItem(item)
                        self._update_model_options()
                        self._load_model_config(m)
                        break
        else:
            QMessageBox.warning(self, "失败", "保存模型配置失败")

    def _on_delete_model(self):
        """删除模型"""
        if not self.current_provider:
            return

        current_item = self.provider_list.currentItem()
        if not current_item:
            return

        data = current_item.data(Qt.UserRole)
        if not isinstance(data, (tuple, list)):
            return

        _, model = data

        reply = QMessageBox.question(
            self,
            "确认删除",
            f'确定要删除模型 "{model.display_name}" 吗？',
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if self.settings_store.remove_model(self.current_provider.id, model.id):
                self.load_providers()
                self._clear_model_config()
                QMessageBox.information(self, "成功", "模型已删除")
