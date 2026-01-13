<script setup lang="ts">
import {
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSwitch,
  NSelect,
  NDivider,
} from 'naive-ui'
import { useSettingsStore } from '@/stores'
import { LANGUAGE_OPTIONS } from '@/types/settings'

const settingsStore = useSettingsStore()

const langOptions = LANGUAGE_OPTIONS.map((l) => ({
  label: l.label,
  value: l.value,
}))
</script>

<template>
  <div v-if="settingsStore.settings" class="translation-tab">
    <NForm label-placement="left" label-width="140">
      <NDivider title-placement="left">语言设置</NDivider>

      <NFormItem label="源语言">
        <NSelect
          v-model:value="settingsStore.settings.translation.langIn"
          :options="langOptions"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="目标语言">
        <NSelect
          v-model:value="settingsStore.settings.translation.langOut"
          :options="langOptions"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">性能设置</NDivider>

      <NFormItem label="QPS 限制">
        <NInputNumber
          v-model:value="settingsStore.settings.translation.qps"
          :min="1"
          :max="100"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="最小文本长度">
        <NInputNumber
          v-model:value="settingsStore.settings.translation.minTextLength"
          :min="1"
          :max="100"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="工作线程数">
        <NInputNumber
          v-model:value="settingsStore.settings.translation.poolMaxWorkers"
          :min="1"
          :max="32"
          placeholder="留空自动"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">翻译行为</NDivider>

      <NFormItem label="自动提取术语表">
        <NSwitch
          v-model:value="settingsStore.settings.translation.autoExtractGlossary"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="保存提取的术语表">
        <NSwitch
          v-model:value="settingsStore.settings.translation.saveAutoExtractedGlossary"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="忽略翻译缓存">
        <NSwitch
          v-model:value="settingsStore.settings.translation.ignoreCache"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="禁用相同文本回退">
        <NSwitch
          v-model:value="settingsStore.settings.translation.disableSameTextFallback"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="添加公式占位符提示">
        <NSwitch
          v-model:value="settingsStore.settings.translation.addFormulaPlaceholdHint"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">自定义提示词</NDivider>

      <NFormItem label="系统提示词">
        <NInput
          v-model:value="settingsStore.settings.translation.customSystemPrompt"
          type="textarea"
          placeholder="自定义系统提示词（留空使用默认）"
          :rows="4"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>
    </NForm>
  </div>
</template>

<style scoped>
.translation-tab {
  padding: 16px 0;
  max-height: 500px;
  overflow-y: auto;
}
</style>
