import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { invoke } from '@tauri-apps/api/core'
import type {
  Settings,
  Provider,
  ModelConfig,
  BUILTIN_PROVIDERS,
} from '@/types/settings'
import { createDefaultSettings } from '@/types/settings'

export const useSettingsStore = defineStore('settings', () => {
  // 状态
  const settings = ref<Settings | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const providers = computed(() => settings.value?.providers.providers ?? [])

  const selectedModelId = computed(
    () => settings.value?.providers.selectedModelId ?? ''
  )

  const selectedModel = computed(() => {
    if (!selectedModelId.value) return null
    for (const provider of providers.value) {
      const model = provider.models.find((m) => m.id === selectedModelId.value)
      if (model) return model
    }
    return null
  })

  const selectedProvider = computed(() => {
    if (!selectedModelId.value) return null
    for (const provider of providers.value) {
      if (provider.models.some((m) => m.id === selectedModelId.value)) {
        return provider
      }
    }
    return null
  })

  const allModelOptions = computed(() => {
    const options: { id: string; label: string; provider: Provider }[] = []
    for (const provider of providers.value) {
      for (const model of provider.models) {
        options.push({
          id: model.id,
          label: `${provider.name} / ${model.displayName}`,
          provider,
        })
      }
    }
    return options
  })

  // 操作方法
  async function loadSettings(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const loaded = await invoke<Settings | null>('load_settings')
      if (loaded) {
        settings.value = loaded
      } else {
        settings.value = createDefaultSettings()
      }
    } catch (e) {
      error.value = String(e)
      settings.value = createDefaultSettings()
    } finally {
      isLoading.value = false
    }
  }

  async function saveSettings(): Promise<void> {
    if (!settings.value) return
    try {
      await invoke('save_settings', { settings: settings.value })
    } catch (e) {
      error.value = String(e)
      throw e
    }
  }

  // 服务商操作
  function addProvider(provider: Provider): void {
    if (!settings.value) return
    settings.value.providers.providers.push(provider)
    saveSettings()
  }

  function updateProvider(providerId: string, updates: Partial<Provider>): void {
    if (!settings.value) return
    const provider = settings.value.providers.providers.find(
      (p) => p.id === providerId
    )
    if (provider) {
      Object.assign(provider, updates)
      saveSettings()
    }
  }

  function removeProvider(providerId: string): void {
    if (!settings.value) return
    const index = settings.value.providers.providers.findIndex(
      (p) => p.id === providerId
    )
    if (index !== -1) {
      // 删除该服务商下的所有模型的选中状态
      const provider = settings.value.providers.providers[index]
      if (
        provider.models.some(
          (m) => m.id === settings.value!.providers.selectedModelId
        )
      ) {
        settings.value.providers.selectedModelId = ''
      }
      settings.value.providers.providers.splice(index, 1)
      saveSettings()
    }
  }

  // 模型操作
  function addModel(providerId: string, model: ModelConfig): void {
    if (!settings.value) return
    const provider = settings.value.providers.providers.find(
      (p) => p.id === providerId
    )
    if (provider) {
      provider.models.push(model)
      saveSettings()
    }
  }

  function updateModel(modelId: string, updates: Partial<ModelConfig>): void {
    if (!settings.value) return
    for (const provider of settings.value.providers.providers) {
      const model = provider.models.find((m) => m.id === modelId)
      if (model) {
        Object.assign(model, updates)
        saveSettings()
        break
      }
    }
  }

  function removeModel(modelId: string): void {
    if (!settings.value) return
    for (const provider of settings.value.providers.providers) {
      const index = provider.models.findIndex((m) => m.id === modelId)
      if (index !== -1) {
        provider.models.splice(index, 1)
        if (settings.value.providers.selectedModelId === modelId) {
          settings.value.providers.selectedModelId = ''
        }
        saveSettings()
        break
      }
    }
  }

  function selectModel(modelId: string): void {
    if (!settings.value) return
    settings.value.providers.selectedModelId = modelId
    saveSettings()
  }

  function getEffectiveBaseUrl(model: ModelConfig): string {
    if (model.baseUrl) return model.baseUrl
    for (const provider of providers.value) {
      if (provider.models.some((m) => m.id === model.id)) {
        return provider.defaultBaseUrl
      }
    }
    return 'https://api.openai.com/v1'
  }

  // 更新翻译设置
  function updateTranslationSettings(
    updates: Partial<Settings['translation']>
  ): void {
    if (!settings.value) return
    Object.assign(settings.value.translation, updates)
    saveSettings()
  }

  // 更新 PDF 设置
  function updatePDFSettings(updates: Partial<Settings['pdf']>): void {
    if (!settings.value) return
    Object.assign(settings.value.pdf, updates)
    saveSettings()
  }

  // 更新路径设置
  function updatePathSettings(updates: Partial<Settings['paths']>): void {
    if (!settings.value) return
    Object.assign(settings.value.paths, updates)
    saveSettings()
  }

  // 更新 RPC 设置
  function updateRPCSettings(updates: Partial<Settings['rpc']>): void {
    if (!settings.value) return
    Object.assign(settings.value.rpc, updates)
    saveSettings()
  }

  // 更新术语提取设置
  function updateTermExtractionSettings(
    updates: Partial<Settings['termExtraction']>
  ): void {
    if (!settings.value) return
    Object.assign(settings.value.termExtraction, updates)
    saveSettings()
  }

  return {
    // 状态
    settings,
    isLoading,
    error,
    // 计算属性
    providers,
    selectedModelId,
    selectedModel,
    selectedProvider,
    allModelOptions,
    // 方法
    loadSettings,
    saveSettings,
    addProvider,
    updateProvider,
    removeProvider,
    addModel,
    updateModel,
    removeModel,
    selectModel,
    getEffectiveBaseUrl,
    updateTranslationSettings,
    updatePDFSettings,
    updatePathSettings,
    updateRPCSettings,
    updateTermExtractionSettings,
  }
})
