<script setup lang="ts">
import { NModal, NCard, NTabs, NTabPane, NButton, NSpace } from 'naive-ui'
import ProviderTab from './tabs/ProviderTab.vue'
import TranslationTab from './tabs/TranslationTab.vue'
import PDFOutputTab from './tabs/PDFOutputTab.vue'
import ProcessingTab from './tabs/ProcessingTab.vue'
import ExpertTab from './tabs/ExpertTab.vue'

const show = defineModel<boolean>('show', { required: true })
</script>

<template>
  <NModal
    v-model:show="show"
    preset="card"
    title="设置"
    :style="{ width: '800px', maxHeight: '80vh' }"
    :mask-closable="false"
  >
    <NTabs type="line" animated>
      <NTabPane name="provider" tab="服务商管理">
        <ProviderTab />
      </NTabPane>

      <NTabPane name="translation" tab="翻译选项">
        <TranslationTab />
      </NTabPane>

      <NTabPane name="pdf" tab="PDF 输出">
        <PDFOutputTab />
      </NTabPane>

      <NTabPane name="processing" tab="文档处理">
        <ProcessingTab />
      </NTabPane>

      <NTabPane name="expert" tab="专家选项">
        <ExpertTab />
      </NTabPane>
    </NTabs>

    <template #footer>
      <NSpace justify="end">
        <NButton @click="show = false">关闭</NButton>
      </NSpace>
    </template>
  </NModal>
</template>
