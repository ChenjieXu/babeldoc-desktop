<script setup lang="ts">
import { ref } from 'vue'
import { NConfigProvider, NMessageProvider, NDialogProvider, zhCN, dateZhCN } from 'naive-ui'
import AppHeader from './components/layout/AppHeader.vue'
import AppSidebar from './components/layout/AppSidebar.vue'
import FileUploader from './components/upload/FileUploader.vue'
import ActionButtons from './components/translation/ActionButtons.vue'
import ProgressDisplay from './components/translation/ProgressDisplay.vue'
import ResultsDisplay from './components/translation/ResultsDisplay.vue'
import SettingsDialog from './components/settings/SettingsDialog.vue'

const showSettings = ref(false)
</script>

<template>
  <NConfigProvider :locale="zhCN" :date-locale="dateZhCN">
    <NMessageProvider>
      <NDialogProvider>
        <div class="app-container">
          <AppHeader @open-settings="showSettings = true" />

          <div class="main-content">
            <AppSidebar />

            <div class="content-area">
              <FileUploader />
              <ActionButtons />
              <ProgressDisplay />
              <ResultsDisplay />
            </div>
          </div>

          <SettingsDialog v-model:show="showSettings" />
        </div>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.content-area {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
