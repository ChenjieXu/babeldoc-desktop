<script setup lang="ts">
import {
  NForm,
  NFormItem,
  NSwitch,
  NInputNumber,
  NSlider,
  NDivider,
} from 'naive-ui'
import { useSettingsStore } from '@/stores'

const settingsStore = useSettingsStore()
</script>

<template>
  <div v-if="settingsStore.settings" class="processing-tab">
    <NForm label-placement="left" label-width="160">
      <NDivider title-placement="left">兼容性设置</NDivider>

      <NFormItem label="增强兼容性模式">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.enhanceCompatibility"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="跳过 PDF 清理">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.skipClean"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">扫描文档与 OCR</NDivider>

      <NFormItem label="跳过扫描检测">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.skipScannedDetection"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="OCR 处理">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.ocrWorkaround"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="自动启用 OCR">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.autoEnableOcrWorkaround"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">文本处理</NDivider>

      <NFormItem label="强制分割短行">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.splitShortLines"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="短行分割因子">
        <NSlider
          v-model:value="settingsStore.settings.pdf.shortLineSplitFactor"
          :min="0.1"
          :max="1.0"
          :step="0.1"
          :disabled="!settingsStore.settings.pdf.splitShortLines"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="合并交替行号">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.mergeAlternatingLineNumbers"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">分段处理</NDivider>

      <NFormItem label="每部分最大页数">
        <NInputNumber
          v-model:value="settingsStore.settings.pdf.maxPagesPerPart"
          :min="1"
          :max="1000"
          placeholder="留空不分段"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">实验性功能</NDivider>

      <NFormItem label="翻译表格文本">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.translateTableText"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="仅解析生成 PDF">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.onlyParseGeneratePdf"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>
    </NForm>
  </div>
</template>

<style scoped>
.processing-tab {
  padding: 16px 0;
  max-height: 500px;
  overflow-y: auto;
}
</style>
