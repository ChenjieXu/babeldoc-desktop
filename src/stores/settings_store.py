"""
设置状态管理
"""

from threading import Lock
from PySide6.QtCore import QObject, Signal
from typing import Optional, List, Dict, Any
from src.models.settings import Settings, Provider, ModelConfig
from src.services.settings_service import SettingsService, get_settings_service


class SettingsStore(QObject):
    """设置状态管理"""

    # 信号
    settings_changed = Signal(dict)  # 设置改变
    providers_changed = Signal(list)  # 服务商列表改变
    selected_model_changed = Signal(str)  # 选中模型改变
    translation_settings_changed = Signal(dict)  # 翻译设置改变
    pdf_settings_changed = Signal(dict)  # PDF 设置改变
    path_settings_changed = Signal(dict)  # 路径设置改变
    term_extraction_settings_changed = Signal(dict)  # 术语提取设置改变
    rpc_settings_changed = Signal(dict)  # RPC 设置改变

    def __init__(self, service: Optional[SettingsService] = None):
        super().__init__()
        self._service = service or get_settings_service()
        self._settings: Optional[Settings] = None

    def load(self) -> Settings:
        """加载设置"""
        self._settings = self._service.load()
        return self._settings

    def save(self):
        """保存设置"""
        if self._settings:
            self._service.save(self._settings)
            data = self._settings_to_dict()
            self.settings_changed.emit(data)

    def replace_settings(self, settings: Settings) -> None:
        """Commit one complete settings snapshot and publish coherent signals."""
        self._service.save(settings)
        self._settings = settings
        self.settings_changed.emit(self._settings_to_dict())
        self.providers_changed.emit(self.get_providers())
        self.selected_model_changed.emit(settings.providers.selected_model_id)
        self.translation_settings_changed.emit({})
        self.pdf_settings_changed.emit({})
        self.path_settings_changed.emit({})
        self.term_extraction_settings_changed.emit({})
        self.rpc_settings_changed.emit({})

    def get_settings(self) -> Settings:
        """获取当前设置"""
        if self._settings is None:
            return self.load()
        return self._settings

    def _settings_to_dict(self) -> Dict[str, Any]:
        """将设置转换为字典"""
        from src.utils.config import settings_to_dict

        return settings_to_dict(self._settings)

    # 服务商相关方法
    def get_providers(self) -> List[Provider]:
        """获取所有服务商"""
        settings = self.get_settings()
        return settings.providers.providers

    def get_provider(self, provider_id: str) -> Optional[Provider]:
        """获取指定服务商"""
        providers = self.get_providers()
        for provider in providers:
            if provider.id == provider_id:
                return provider
        return None

    def add_provider(self, provider: Provider) -> bool:
        """添加服务商"""
        if self._service.add_provider(provider):
            self._settings = self._service.get_settings()
            self.providers_changed.emit(self.get_providers())
            return True
        return False

    def update_provider(self, provider_id: str, provider: Provider) -> bool:
        """更新服务商"""
        if self._service.update_provider(provider_id, provider):
            self._settings = self._service.get_settings()
            self.providers_changed.emit(self.get_providers())
            return True
        return False

    def remove_provider(self, provider_id: str) -> bool:
        """删除服务商"""
        if self._service.remove_provider(provider_id):
            self._settings = self._service.get_settings()
            self.providers_changed.emit(self.get_providers())
            return True
        return False

    # 模型相关方法
    def add_model(self, provider_id: str, model: ModelConfig) -> bool:
        """添加模型"""
        if self._service.add_model(provider_id, model):
            self._settings = self._service.get_settings()
            self.providers_changed.emit(self.get_providers())
            return True
        return False

    def update_model(self, provider_id: str, model_id: str, model: ModelConfig) -> bool:
        """更新模型"""
        if self._service.update_model(provider_id, model_id, model):
            self._settings = self._service.get_settings()
            self.providers_changed.emit(self.get_providers())
            return True
        return False

    def remove_model(self, provider_id: str, model_id: str) -> bool:
        """删除模型"""
        if self._service.remove_model(provider_id, model_id):
            self._settings = self._service.get_settings()
            self.providers_changed.emit(self.get_providers())
            return True
        return False

    def get_selected_model(self) -> Optional[ModelConfig]:
        """获取选中的模型"""
        return self._service.get_selected_model()

    def select_model(self, model_id: str) -> bool:
        """选中模型"""
        if self._service.select_model(model_id):
            self._settings = self._service.get_settings()
            self.selected_model_changed.emit(model_id)
            return True
        return False

    def get_all_models(self) -> List[Dict[str, Any]]:
        """获取所有模型（包含服务商信息）"""
        return self._service.get_all_models()

    # 翻译设置相关方法
    def update_translation_settings(self, **kwargs) -> bool:
        """更新翻译设置"""
        if self._service.update_translation_settings(**kwargs):
            self._settings = self._service.get_settings()
            self.translation_settings_changed.emit(kwargs)
            return True
        return False

    # PDF 设置相关方法
    def update_pdf_settings(self, **kwargs) -> bool:
        """更新 PDF 设置"""
        if self._service.update_pdf_settings(**kwargs):
            self._settings = self._service.get_settings()
            self.pdf_settings_changed.emit(kwargs)
            return True
        return False

    # 路径设置相关方法
    def update_path_settings(self, **kwargs) -> bool:
        """更新路径设置"""
        if self._service.update_path_settings(**kwargs):
            self._settings = self._service.get_settings()
            self.path_settings_changed.emit(kwargs)
            return True
        return False

    # 术语提取设置相关方法
    def update_term_extraction_settings(self, **kwargs) -> bool:
        """更新术语提取设置"""
        if self._service.update_term_extraction_settings(**kwargs):
            self._settings = self._service.get_settings()
            self.term_extraction_settings_changed.emit(kwargs)
            return True
        return False

    # RPC 设置相关方法
    def update_rpc_settings(self, **kwargs) -> bool:
        """更新 RPC 设置"""
        if self._service.update_rpc_settings(**kwargs):
            self._settings = self._service.get_settings()
            self.rpc_settings_changed.emit(kwargs)
            return True
        return False


# 全局单例
_settings_store: Optional[SettingsStore] = None
_store_lock = Lock()  # 单例线程安全锁


def get_settings_store() -> SettingsStore:
    """获取设置状态管理单例（线程安全）"""
    global _settings_store
    if _settings_store is None:
        with _store_lock:
            if _settings_store is None:
                _settings_store = SettingsStore()
    return _settings_store
