<script setup lang="ts">
import { computed, onMounted } from 'vue'
import {
  NSelect,
  NInput,
  NSwitch,
  NCollapse,
  NCollapseItem,
  NFormItem,
  NSpace,
} from 'naive-ui'
import { useSettingsStore, useTranslationStore } from '@/stores'
import { LANGUAGE_OPTIONS } from '@/types/settings'

const settingsStore = useSettingsStore()
const translationStore = useTranslationStore()

onMounted(() => {
  settingsStore.loadSettings()
})

// 语言选项
const langInOptions = LANGUAGE_OPTIONS.map((l) => ({
  label: l.label,
  value: l.value,
}))

const langOutOptions = LANGUAGE_OPTIONS.map((l) => ({
  label: l.label,
  value: l.value,
}))

// 模型选项
const modelOptions = computed(() =>
  settingsStore.allModelOptions.map((m) => ({
    label: m.label,
    value: m.id,
  }))
)

// 页码范围
const pages = computed({
  get: () => settingsStore.settings?.translation?.langIn || '',
  set: () => {},
})
</script>

<template>
  <aside class="app-sidebar">
    <div class="sidebar-header">
      <h3>翻译选项</h3>
    </div>

    <div class="sidebar-content">
      <NSpace vertical :size="16">
        <!-- 源语言 -->
        <NFormItem label="源语言" label-placement="left">
          <NSelect
            v-if="settingsStore.settings"
            v-model:value="settingsStore.settings.translation.langIn"
            :options="langInOptions"
            placeholder="选择源语言"
            @update:value="settingsStore.saveSettings()"
          />
        </NFormItem>

        <!-- 目标语言 -->
        <NFormItem label="目标语言" label-placement="left">
          <NSelect
            v-if="settingsStore.settings"
            v-model:value="settingsStore.settings.translation.langOut"
            :options="langOutOptions"
            placeholder="选择目标语言"
            @update:value="settingsStore.saveSettings()"
          />
        </NFormItem>

        <!-- 模型选择 -->
        <NFormItem label="翻译模型" label-placement="top">
          <NSelect
            v-if="settingsStore.settings"
            v-model:value="settingsStore.settings.providers.selectedModelId"
            :options="modelOptions"
            placeholder="选择模型"
            filterable
            @update:value="settingsStore.saveSettings()"
          />
        </NFormItem>

        <!-- 页码范围 -->
        <NFormItem label="页码范围" label-placement="top">
          <NInput placeholder="例如: 1,2,3-5 (留空翻译全部)" />
        </NFormItem>

        <!-- 快速选项 -->
        <NCollapse>
          <NCollapseItem title="更多选项" name="more">
            <NSpace vertical :size="12">
              <!-- 输出格式 -->
              <NFormItem label="输出双语 PDF" label-placement="left">
                <NSwitch
                  v-if="settingsStore.settings"
                  v-model:value="settingsStore.settings.pdf.outputDual"
                  @update:value="settingsStore.saveSettings()"
                />
              </NFormItem>

              <NFormItem label="输出单语 PDF" label-placement="left">
                <NSwitch
                  v-if="settingsStore.settings"
                  v-model:value="settingsStore.settings.pdf.outputMono"
                  @update:value="settingsStore.saveSettings()"
                />
              </NFormItem>

              <!-- 兼容性 -->
              <NFormItem label="增强兼容性" label-placement="left">
                <NSwitch
                  v-if="settingsStore.settings"
                  v-model:value="settingsStore.settings.pdf.enhanceCompatibility"
                  @update:value="settingsStore.saveSettings()"
                />
              </NFormItem>

              <!-- 术语提取 -->
              <NFormItem label="自动提取术语" label-placement="left">
                <NSwitch
                  v-if="settingsStore.settings"
                  v-model:value="settingsStore.settings.translation.autoExtractGlossary"
                  @update:value="settingsStore.saveSettings()"
                />
              </NFormItem>
            </NSpace>
          </NCollapseItem>
        </NCollapse>
      </NSpace>
    </div>
  </aside>
</template>

<style scoped>
.app-sidebar {
  width: 260px;
  background-color: #fff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.sidebar-content {
  padding: 16px 20px;
  overflow-y: auto;
  flex: 1;
}

:deep(.n-form-item) {
  margin-bottom: 0;
}

:deep(.n-form-item-label) {
  font-size: 13px;
}
</style>
