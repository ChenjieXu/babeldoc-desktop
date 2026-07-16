"""
设置服务
"""

from threading import Lock
from typing import Optional, List, Dict, Any
from src.models.settings import Settings, Provider, ModelConfig, create_default_settings
from src.utils.config import (
    load_settings,
    save_settings,
    dict_to_settings,
    settings_to_dict,
)


class SettingsService:
    """设置服务"""

    def __init__(
        self, initial_settings: Optional[Settings] = None, *, persist: bool = True
    ):
        self._settings = initial_settings
        self._persist = persist

    def load(self) -> Settings:
        """加载设置"""
        if self._settings is None:
            data = load_settings()
            self._settings = dict_to_settings(data)
        return self._settings

    def save(self, settings: Settings):
        """保存设置"""
        if self._persist:
            data = settings_to_dict(settings)
            save_settings(data)
        self._settings = settings

    def reset_to_default(self) -> Settings:
        """重置为默认设置"""
        self._settings = create_default_settings()
        self.save(self._settings)
        return self._settings

    def get_settings(self) -> Settings:
        """获取当前设置"""
        if self._settings is None:
            return self.load()
        return self._settings

    # 服务商相关方法
    def get_providers(self) -> List[Provider]:
        """获取所有服务商"""
        return self.get_settings().providers.providers

    def get_provider(self, provider_id: str) -> Optional[Provider]:
        """获取指定服务商"""
        for provider in self.get_providers():
            if provider.id == provider_id:
                return provider
        return None

    def add_provider(self, provider: Provider) -> bool:
        """添加服务商"""
        settings = self.get_settings()
        if any(p.id == provider.id for p in settings.providers.providers):
            return False
        settings.providers.providers.append(provider)
        self.save(settings)
        return True

    def update_provider(self, provider_id: str, provider: Provider) -> bool:
        """更新服务商"""
        settings = self.get_settings()
        for i, p in enumerate(settings.providers.providers):
            if p.id == provider_id:
                settings.providers.providers[i] = provider
                self.save(settings)
                return True
        return False

    def remove_provider(self, provider_id: str) -> bool:
        """删除服务商"""
        settings = self.get_settings()
        for i, p in enumerate(settings.providers.providers):
            if p.id == provider_id:
                if p.is_builtin:
                    return False
                settings.providers.providers.pop(i)
                self.save(settings)
                return True
        return False

    def _find_model(
        self, provider_id: str, model_id: str
    ) -> tuple[Optional[Provider], Optional[ModelConfig]]:
        """查找模型"""
        for provider in self.get_settings().providers.providers:
            if provider.id == provider_id:
                for model in provider.models:
                    if model.id == model_id:
                        return provider, model
        return None, None

    def add_model(self, provider_id: str, model: ModelConfig) -> bool:
        """添加模型"""
        settings = self.get_settings()
        for provider in settings.providers.providers:
            if provider.id == provider_id:
                provider.models.append(model)
                self.save(settings)
                return True
        return False

    def update_model(self, provider_id: str, model_id: str, model: ModelConfig) -> bool:
        """更新模型"""
        settings = self.get_settings()
        for provider in settings.providers.providers:
            if provider.id == provider_id:
                for i, m in enumerate(provider.models):
                    if m.id == model_id:
                        provider.models[i] = model
                        self.save(settings)
                        return True
        return False

    def remove_model(self, provider_id: str, model_id: str) -> bool:
        """删除模型"""
        settings = self.get_settings()
        for provider in settings.providers.providers:
            if provider.id == provider_id:
                for i, m in enumerate(provider.models):
                    if m.id == model_id:
                        provider.models.pop(i)
                        self.save(settings)
                        return True
        return False

    def get_selected_model(self) -> Optional[ModelConfig]:
        """获取选中的模型"""
        selected_id = self.get_settings().providers.selected_model_id
        if not selected_id:
            return None
        for provider in self.get_settings().providers.providers:
            for model in provider.models:
                if model.id == selected_id:
                    return model
        return None

    def select_model(self, model_id: str) -> bool:
        """选中模型"""
        settings = self.get_settings()
        for provider in settings.providers.providers:
            for model in provider.models:
                if model.id == model_id:
                    if settings.providers.selected_model_id == model_id:
                        return True
                    settings.providers.selected_model_id = model_id
                    self.save(settings)
                    return True
        return False

    def get_all_models(self) -> List[Dict[str, Any]]:
        """获取所有模型（包含服务商信息）"""
        return [
            {"model": model, "provider": provider}
            for provider in self.get_settings().providers.providers
            for model in provider.models
        ]

    def _update_setting(self, section: str, **kwargs) -> bool:
        """通用设置更新方法"""
        settings = self.get_settings()
        target = getattr(settings, section, None)
        if not target:
            return False

        for key, value in kwargs.items():
            if hasattr(target, key):
                setattr(target, key, value)

        self.save(settings)
        return True

    def update_translation_settings(self, **kwargs) -> bool:
        """更新翻译设置"""
        return self._update_setting("translation", **kwargs)

    def update_pdf_settings(self, **kwargs) -> bool:
        """更新 PDF 设置"""
        return self._update_setting("pdf", **kwargs)

    def update_path_settings(self, **kwargs) -> bool:
        """更新路径设置"""
        return self._update_setting("paths", **kwargs)

    def update_term_extraction_settings(self, **kwargs) -> bool:
        """更新术语提取设置"""
        return self._update_setting("term_extraction", **kwargs)

    def update_rpc_settings(self, **kwargs) -> bool:
        """更新 RPC 设置"""
        return self._update_setting("rpc", **kwargs)


# 全局单例
_settings_service: Optional[SettingsService] = None
_service_lock = Lock()  # 单例线程安全锁


def get_settings_service() -> SettingsService:
    """获取设置服务单例（线程安全）"""
    global _settings_service
    if _settings_service is None:
        with _service_lock:
            if _settings_service is None:
                _settings_service = SettingsService()
    return _settings_service
