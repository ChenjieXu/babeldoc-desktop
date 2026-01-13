<script setup lang="ts">
import { NCard, NButton, NIcon, NTag, NSpace, NText } from 'naive-ui'
import { DocumentOutline, FolderOpenOutline, DownloadOutline } from '@vicons/ionicons5'
import { invoke } from '@tauri-apps/api/core'
import { useTranslationStore } from '@/stores'

const translationStore = useTranslationStore()

// 打开文件位置
async function openFileLocation(path: string) {
  try {
    await invoke('open_file_location', { path })
  } catch (e) {
    console.error('Failed to open location:', e)
  }
}
</script>

<template>
  <NCard v-if="translationStore.hasResults" class="results-card">
    <template #header>
      <div class="results-header">
        <NText strong>翻译结果</NText>
        <NTag type="success" size="small">
          {{ translationStore.resultFiles.length }} 个文件
        </NTag>
      </div>
    </template>

    <div class="results-list">
      <div
        v-for="(file, index) in translationStore.resultFiles"
        :key="index"
        class="result-item"
      >
        <div class="result-info">
          <NIcon size="20" color="#1890ff">
            <DocumentOutline />
          </NIcon>
          <div class="result-details">
            <span class="result-name">{{ file.name }}</span>
            <NTag size="small" :bordered="false">{{ file.type }}</NTag>
          </div>
        </div>

        <NSpace>
          <NButton
            quaternary
            size="small"
            @click="openFileLocation(file.path)"
          >
            <template #icon>
              <NIcon>
                <FolderOpenOutline />
              </NIcon>
            </template>
            打开位置
          </NButton>
        </NSpace>
      </div>
    </div>
  </NCard>
</template>

<style scoped>
.results-card {
  background-color: #fff;
}

.results-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #f6ffed;
  border-radius: 6px;
  border: 1px solid #b7eb8f;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-details {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-name {
  font-size: 14px;
  color: #333;
}
</style>
