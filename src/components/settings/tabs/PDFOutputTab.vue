<script setup lang="ts">
import {
  NForm,
  NFormItem,
  NSwitch,
  NSelect,
  NDivider,
} from 'naive-ui'
import { useSettingsStore } from '@/stores'

const settingsStore = useSettingsStore()

const watermarkOptions = [
  { label: '有水印', value: 'watermarked' },
  { label: '无水印', value: 'no_watermark' },
  { label: '两者都输出', value: 'both' },
]

const fontFamilyOptions = [
  { label: '自动', value: null },
  { label: '衬线字体 (Serif)', value: 'serif' },
  { label: '无衬线字体 (Sans-serif)', value: 'sans-serif' },
  { label: '手写字体 (Script)', value: 'script' },
]
</script>

<template>
  <div v-if="settingsStore.settings" class="pdf-output-tab">
    <NForm label-placement="left" label-width="140">
      <NDivider title-placement="left">输出格式</NDivider>

      <NFormItem label="输出双语 PDF">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.outputDual"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="输出单语 PDF">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.outputMono"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="水印模式">
        <NSelect
          v-model:value="settingsStore.settings.pdf.watermarkMode"
          :options="watermarkOptions"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">双语 PDF 设置</NDivider>

      <NFormItem label="翻译页在前">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.dualTranslateFirst"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="交替页面模式">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.useAlternatingPagesDual"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="仅包含翻译页">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.onlyIncludeTranslatedPage"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">字体设置</NDivider>

      <NFormItem label="主字体族">
        <NSelect
          v-model:value="settingsStore.settings.pdf.primaryFontFamily"
          :options="fontFamilyOptions"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="禁用富文本翻译">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.disableRichTextTranslate"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>
    </NForm>
  </div>
</template>

<style scoped>
.pdf-output-tab {
  padding: 16px 0;
  max-height: 500px;
  overflow-y: auto;
}
</style>
