<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  NCard,
  NButton,
  NIcon,
  NSpace,
  NCollapse,
  NCollapseItem,
  NList,
  NListItem,
  NThing,
  NTag,
  NInput,
  NInputGroup,
  NSwitch,
  NModal,
  NForm,
  NFormItem,
  useMessage,
} from 'naive-ui'
import { Add, TrashOutline, CreateOutline } from '@vicons/ionicons5'
import { useSettingsStore } from '@/stores'
import type { ModelConfig, Provider } from '@/types/settings'
import { BUILTIN_PROVIDERS } from '@/types/settings'

const settingsStore = useSettingsStore()
const message = useMessage()

// 添加模型对话框
const showAddModel = ref(false)
const editingProviderId = ref<string>('')
const newModel = ref<Partial<ModelConfig>>({
  displayName: '',
  modelName: '',
  apiKey: '',
  baseUrl: '',
  enableJsonMode: false,
  sendDashscopeHeader: false,
  noSendTemperature: false,
})

// 添加自定义服务商对话框
const showAddProvider = ref(false)
const newProvider = ref({
  name: '',
  defaultBaseUrl: '',
})

// 打开添加模型对话框
function openAddModel(providerId: string) {
  editingProviderId.value = providerId
  newModel.value = {
    displayName: '',
    modelName: '',
    apiKey: '',
    baseUrl: '',
    enableJsonMode: false,
    sendDashscopeHeader: false,
    noSendTemperature: false,
  }
  showAddModel.value = true
}

// 保存模型
function saveModel() {
  if (!newModel.value.displayName || !newModel.value.modelName || !newModel.value.apiKey) {
    message.error('请填写必填项')
    return
  }

  const model: ModelConfig = {
    id: crypto.randomUUID(),
    displayName: newModel.value.displayName!,
    modelName: newModel.value.modelName!,
    apiKey: newModel.value.apiKey!,
    baseUrl: newModel.value.baseUrl || null,
    enableJsonMode: newModel.value.enableJsonMode || false,
    sendDashscopeHeader: newModel.value.sendDashscopeHeader || false,
    noSendTemperature: newModel.value.noSendTemperature || false,
  }

  settingsStore.addModel(editingProviderId.value, model)
  showAddModel.value = false
  message.success('模型已添加')
}

// 删除模型
function deleteModel(modelId: string) {
  settingsStore.removeModel(modelId)
  message.success('模型已删除')
}

// 添加自定义服务商
function saveProvider() {
  if (!newProvider.value.name || !newProvider.value.defaultBaseUrl) {
    message.error('请填写必填项')
    return
  }

  const provider: Provider = {
    id: crypto.randomUUID(),
    name: newProvider.value.name,
    defaultBaseUrl: newProvider.value.defaultBaseUrl,
    isBuiltin: false,
    icon: 'server',
    models: [],
  }

  settingsStore.addProvider(provider)
  showAddProvider.value = false
  newProvider.value = { name: '', defaultBaseUrl: '' }
  message.success('服务商已添加')
}

// 删除自定义服务商
function deleteProvider(providerId: string) {
  settingsStore.removeProvider(providerId)
  message.success('服务商已删除')
}
</script>

<template>
  <div class="provider-tab">
    <div class="tab-header">
      <NButton type="primary" @click="showAddProvider = true">
        <template #icon>
          <NIcon><Add /></NIcon>
        </template>
        添加自定义服务商
      </NButton>
    </div>

    <NCollapse>
      <NCollapseItem
        v-for="provider in settingsStore.providers"
        :key="provider.id"
        :title="provider.name"
        :name="provider.id"
      >
        <template #header-extra>
          <NSpace>
            <NTag v-if="provider.isBuiltin" size="small" type="info">内置</NTag>
            <NTag size="small">{{ provider.models.length }} 个模型</NTag>
          </NSpace>
        </template>

        <div class="provider-content">
          <div class="provider-info">
            <span class="label">默认 Base URL:</span>
            <code>{{ provider.defaultBaseUrl }}</code>
          </div>

          <div class="provider-actions">
            <NButton size="small" @click="openAddModel(provider.id)">
              <template #icon>
                <NIcon><Add /></NIcon>
              </template>
              添加模型
            </NButton>
            <NButton
              v-if="!provider.isBuiltin"
              size="small"
              type="error"
              @click="deleteProvider(provider.id)"
            >
              <template #icon>
                <NIcon><TrashOutline /></NIcon>
              </template>
              删除服务商
            </NButton>
          </div>

          <NList v-if="provider.models.length > 0" bordered>
            <NListItem v-for="model in provider.models" :key="model.id">
              <NThing :title="model.displayName" :description="model.modelName">
                <template #header-extra>
                  <NTag
                    v-if="settingsStore.selectedModelId === model.id"
                    type="success"
                    size="small"
                  >
                    已选中
                  </NTag>
                </template>
                <template #action>
                  <NSpace>
                    <NButton
                      size="small"
                      :type="settingsStore.selectedModelId === model.id ? 'primary' : 'default'"
                      @click="settingsStore.selectModel(model.id)"
                    >
                      {{ settingsStore.selectedModelId === model.id ? '已选中' : '选择' }}
                    </NButton>
                    <NButton size="small" type="error" @click="deleteModel(model.id)">
                      删除
                    </NButton>
                  </NSpace>
                </template>
              </NThing>
            </NListItem>
          </NList>

          <div v-else class="no-models">
            暂无模型，点击上方按钮添加
          </div>
        </div>
      </NCollapseItem>
    </NCollapse>

    <!-- 添加模型对话框 -->
    <NModal v-model:show="showAddModel" preset="card" title="添加模型" style="width: 500px">
      <NForm label-placement="left" label-width="100">
        <NFormItem label="显示名称" required>
          <NInput v-model:value="newModel.displayName" placeholder="例如: GPT-4o Mini" />
        </NFormItem>
        <NFormItem label="模型名称" required>
          <NInput v-model:value="newModel.modelName" placeholder="例如: gpt-4o-mini" />
        </NFormItem>
        <NFormItem label="API Key" required>
          <NInput
            v-model:value="newModel.apiKey"
            type="password"
            show-password-on="click"
            placeholder="输入 API Key"
          />
        </NFormItem>
        <NFormItem label="自定义 Base URL">
          <NInput v-model:value="newModel.baseUrl" placeholder="留空使用服务商默认 URL" />
        </NFormItem>
        <NFormItem label="启用 JSON 模式">
          <NSwitch v-model:value="newModel.enableJsonMode" />
        </NFormItem>
        <NFormItem label="发送 DashScope Header">
          <NSwitch v-model:value="newModel.sendDashscopeHeader" />
        </NFormItem>
        <NFormItem label="不发送 Temperature">
          <NSwitch v-model:value="newModel.noSendTemperature" />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="showAddModel = false">取消</NButton>
          <NButton type="primary" @click="saveModel">保存</NButton>
        </NSpace>
      </template>
    </NModal>

    <!-- 添加服务商对话框 -->
    <NModal v-model:show="showAddProvider" preset="card" title="添加自定义服务商" style="width: 500px">
      <NForm label-placement="left" label-width="100">
        <NFormItem label="服务商名称" required>
          <NInput v-model:value="newProvider.name" placeholder="例如: 自定义 API" />
        </NFormItem>
        <NFormItem label="Base URL" required>
          <NInput v-model:value="newProvider.defaultBaseUrl" placeholder="例如: https://api.example.com/v1" />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="showAddProvider = false">取消</NButton>
          <NButton type="primary" @click="saveProvider">保存</NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

<style scoped>
.provider-tab {
  padding: 16px 0;
}

.tab-header {
  margin-bottom: 16px;
}

.provider-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.provider-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.provider-info .label {
  color: #666;
}

.provider-info code {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.provider-actions {
  display: flex;
  gap: 8px;
}

.no-models {
  padding: 24px;
  text-align: center;
  color: #999;
  background-color: #fafafa;
  border-radius: 6px;
}
</style>
