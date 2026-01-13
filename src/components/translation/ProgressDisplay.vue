<script setup lang="ts">
import { computed } from 'vue'
import { NProgress, NText, NCard } from 'naive-ui'
import { useTranslationStore } from '@/stores'

const translationStore = useTranslationStore()

// 是否显示进度
const showProgress = computed(() => {
  return translationStore.isRunning || translationStore.progress > 0
})
</script>

<template>
  <NCard v-if="showProgress" class="progress-card">
    <div class="progress-header">
      <NText strong>翻译进度</NText>
      <NText>{{ translationStore.progressPercent }}%</NText>
    </div>

    <NProgress
      type="line"
      :percentage="translationStore.progress"
      :show-indicator="false"
      :height="8"
      :border-radius="4"
      :status="translationStore.error ? 'error' : 'default'"
    />

    <div class="progress-info">
      <NText depth="3">
        {{ translationStore.stage }}
        <template v-if="translationStore.stageTotal > 0">
          ({{ translationStore.stageCurrent }}/{{ translationStore.stageTotal }})
        </template>
      </NText>
    </div>

    <div v-if="translationStore.error" class="progress-error">
      <NText type="error">{{ translationStore.error }}</NText>
    </div>
  </NCard>
</template>

<style scoped>
.progress-card {
  background-color: #fff;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-info {
  margin-top: 8px;
}

.progress-error {
  margin-top: 12px;
  padding: 8px 12px;
  background-color: #fff2f0;
  border-radius: 4px;
}
</style>
