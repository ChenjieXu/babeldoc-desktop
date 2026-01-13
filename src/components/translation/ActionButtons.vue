<script setup lang="ts">
import { computed } from 'vue'
import { NButton, NSpace, useMessage } from 'naive-ui'
import { useSettingsStore, useTranslationStore } from '@/stores'
import type { TranslationConfig } from '@/types/events'

const settingsStore = useSettingsStore()
const translationStore = useTranslationStore()
const message = useMessage()

// 是否可以开始翻译
const canStart = computed(() => {
  return (
    translationStore.hasFiles &&
    settingsStore.selectedModel &&
    !translationStore.isRunning
  )
})

// 开始翻译
async function startTranslation() {
  if (!settingsStore.selectedModel || !settingsStore.settings) {
    message.error('请先选择翻译模型')
    return
  }

  if (translationStore.uploadedFiles.length === 0) {
    message.error('请先上传 PDF 文件')
    return
  }

  const model = settingsStore.selectedModel
  const settings = settingsStore.settings

  // 对每个文件启动翻译
  for (const file of translationStore.uploadedFiles) {
    const config: TranslationConfig = {
      inputFile: file.path,
      langIn: settings.translation.langIn,
      langOut: settings.translation.langOut,
      model: model.modelName,
      apiKey: model.apiKey,
      baseUrl: settingsStore.getEffectiveBaseUrl(model),
      outputDual: settings.pdf.outputDual,
      outputMono: settings.pdf.outputMono,
      watermarkMode: settings.pdf.watermarkMode,
      enhanceCompatibility: settings.pdf.enhanceCompatibility,
      skipClean: settings.pdf.skipClean,
      qps: settings.translation.qps,
      autoExtractGlossary: settings.translation.autoExtractGlossary,
      ignoreCache: settings.translation.ignoreCache,
      enableJsonMode: model.enableJsonMode,
      sendDashscopeHeader: model.sendDashscopeHeader,
      noSendTemperature: model.noSendTemperature,
    }

    try {
      await translationStore.startTranslation(config)
    } catch (e) {
      message.error(`翻译失败: ${e}`)
    }
  }
}

// 取消翻译
async function cancelTranslation() {
  await translationStore.cancelTranslation()
  message.info('翻译已取消')
}
</script>

<template>
  <div class="action-buttons">
    <NSpace>
      <NButton
        v-if="!translationStore.isRunning"
        type="primary"
        size="large"
        :disabled="!canStart"
        @click="startTranslation"
      >
        开始翻译
      </NButton>

      <NButton
        v-else
        type="error"
        size="large"
        @click="cancelTranslation"
      >
        取消翻译
      </NButton>
    </NSpace>
  </div>
</template>

<style scoped>
.action-buttons {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}
</style>
