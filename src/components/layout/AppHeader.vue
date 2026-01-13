<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui'
import { Settings } from '@vicons/ionicons5'

defineEmits<{
  (e: 'open-settings'): void
}>()
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <h1 class="app-title">BabelDOC</h1>
      <span class="app-version">v0.1.0</span>
    </div>

    <div class="header-right">
      <NButton quaternary circle @click="$emit('open-settings')">
        <template #icon>
          <NIcon size="20">
            <Settings />
          </NIcon>
        </template>
      </NButton>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 20px;
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.app-version {
  font-size: 12px;
  color: #999;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
