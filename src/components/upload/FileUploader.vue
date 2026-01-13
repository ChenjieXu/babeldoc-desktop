<script setup lang="ts">
import { ref } from 'vue'
import { NUpload, NUploadDragger, NIcon, NText, NButton, NSpace } from 'naive-ui'
import { CloudUploadOutline, DocumentOutline, TrashOutline } from '@vicons/ionicons5'
import { open } from '@tauri-apps/plugin-dialog'
import { invoke } from '@tauri-apps/api/core'
import { useTranslationStore } from '@/stores'

const translationStore = useTranslationStore()

// 选择文件
async function selectFiles() {
  try {
    const selected = await open({
      multiple: true,
      filters: [
        {
          name: 'PDF 文件',
          extensions: ['pdf'],
        },
      ],
    })

    if (selected) {
      const paths = Array.isArray(selected) ? selected : [selected]
      for (const path of paths) {
        // 获取文件信息
        const info = await invoke<{ name: string; path: string; size: number }>(
          'get_file_info',
          { path }
        )
        translationStore.addFile({
          id: crypto.randomUUID(),
          name: info.name,
          path: info.path,
          size: info.size,
        })
      }
    }
  } catch (e) {
    console.error('Failed to select files:', e)
  }
}

// 格式化文件大小
function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<template>
  <div class="file-uploader">
    <!-- 上传区域 -->
    <div class="upload-area" @click="selectFiles">
      <NIcon size="48" color="#999">
        <CloudUploadOutline />
      </NIcon>
      <NText class="upload-text">点击或拖拽 PDF 文件到此处</NText>
      <NText depth="3" class="upload-hint">支持多个文件同时上传</NText>
    </div>

    <!-- 文件列表 -->
    <div v-if="translationStore.uploadedFiles.length > 0" class="file-list">
      <div
        v-for="file in translationStore.uploadedFiles"
        :key="file.id"
        class="file-item"
      >
        <div class="file-info">
          <NIcon size="20" color="#1890ff">
            <DocumentOutline />
          </NIcon>
          <div class="file-details">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatSize(file.size) }}</span>
          </div>
        </div>
        <NButton
          quaternary
          circle
          size="small"
          @click="translationStore.removeFile(file.id)"
        >
          <template #icon>
            <NIcon>
              <TrashOutline />
            </NIcon>
          </template>
        </NButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.file-uploader {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #1890ff;
  background-color: #fafafa;
}

.upload-text {
  margin-top: 16px;
  font-size: 16px;
  color: #333;
}

.upload-hint {
  margin-top: 8px;
  font-size: 13px;
}

.file-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #fafafa;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.file-name {
  font-size: 14px;
  color: #333;
}

.file-size {
  font-size: 12px;
  color: #999;
}
</style>
