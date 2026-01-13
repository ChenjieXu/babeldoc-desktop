<script setup lang="ts">
import {
  NForm,
  NFormItem,
  NInput,
  NSwitch,
  NSlider,
  NDivider,
} from 'naive-ui'
import { useSettingsStore } from '@/stores'

const settingsStore = useSettingsStore()
</script>

<template>
  <div v-if="settingsStore.settings" class="expert-tab">
    <NForm label-placement="left" label-width="180">
      <NDivider title-placement="left">渲染选项</NDivider>

      <NFormItem label="跳过表单渲染">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.skipFormRender"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="跳过曲线渲染">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.skipCurveRender"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="移除非公式线条">
        <NSwitch
          v-model:value="settingsStore.settings.pdf.removeNonFormulaLines"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="非公式线条 IoU 阈值">
        <NSlider
          v-model:value="settingsStore.settings.pdf.nonFormulaLineIouThreshold"
          :min="0"
          :max="1"
          :step="0.05"
          :disabled="!settingsStore.settings.pdf.removeNonFormulaLines"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="图表保护阈值">
        <NSlider
          v-model:value="settingsStore.settings.pdf.figureTableProtectionThreshold"
          :min="0"
          :max="1"
          :step="0.05"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">公式匹配</NDivider>

      <NFormItem label="公式字体匹配模式">
        <NInput
          v-model:value="settingsStore.settings.pdf.formularFontPattern"
          placeholder="正则表达式"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="公式字符匹配模式">
        <NInput
          v-model:value="settingsStore.settings.pdf.formularCharPattern"
          placeholder="正则表达式"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">路径设置</NDivider>

      <NFormItem label="输出目录">
        <NInput
          v-model:value="settingsStore.settings.paths.outputDir"
          placeholder="留空使用默认"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="工作目录">
        <NInput
          v-model:value="settingsStore.settings.paths.workingDir"
          placeholder="留空使用默认"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NFormItem label="术语表文件">
        <NInput
          v-model:value="settingsStore.settings.paths.glossaryFiles"
          placeholder="多个文件用逗号分隔"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>

      <NDivider title-placement="left">RPC 服务</NDivider>

      <NFormItem label="DocLayout RPC 地址">
        <NInput
          v-model:value="settingsStore.settings.rpc.doclayoutHost"
          placeholder="例如: localhost:50051"
          @update:value="settingsStore.saveSettings()"
        />
      </NFormItem>
    </NForm>
  </div>
</template>

<style scoped>
.expert-tab {
  padding: 16px 0;
  max-height: 500px;
  overflow-y: auto;
}
</style>
