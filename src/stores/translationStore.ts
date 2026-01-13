import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { invoke } from '@tauri-apps/api/core'
import { listen, type UnlistenFn } from '@tauri-apps/api/event'
import type {
  TranslationEvent,
  TranslationConfig,
  UploadedFile,
  ResultFile,
} from '@/types/events'

export const useTranslationStore = defineStore('translation', () => {
  // 状态
  const isRunning = ref(false)
  const progress = ref(0)
  const stage = ref('')
  const stageCurrent = ref(0)
  const stageTotal = ref(0)
  const currentFile = ref<string | null>(null)
  const error = ref<string | null>(null)
  const resultFiles = ref<ResultFile[]>([])
  const uploadedFiles = ref<UploadedFile[]>([])

  // 私有状态
  let currentTaskId: string | null = null
  let unlistenFn: UnlistenFn | null = null

  // 计算属性
  const hasFiles = computed(() => uploadedFiles.value.length > 0)
  const hasResults = computed(() => resultFiles.value.length > 0)
  const progressPercent = computed(() => Math.round(progress.value))

  // 文件操作
  function addFile(file: UploadedFile): void {
    // 避免重复添加
    if (!uploadedFiles.value.some((f) => f.path === file.path)) {
      uploadedFiles.value.push(file)
    }
  }

  function removeFile(fileId: string): void {
    const index = uploadedFiles.value.findIndex((f) => f.id === fileId)
    if (index !== -1) {
      uploadedFiles.value.splice(index, 1)
    }
  }

  function clearFiles(): void {
    uploadedFiles.value = []
  }

  // 处理翻译事件
  function handleEvent(event: TranslationEvent): void {
    switch (event.type) {
      case 'progress_update':
        progress.value = event.overallProgress
        stage.value = event.stage
        stageCurrent.value = event.stageCurrent
        stageTotal.value = event.stageTotal
        break

      case 'finish':
        isRunning.value = false
        progress.value = 100
        stage.value = '完成'
        processResult(event.translateResult)
        cleanup()
        break

      case 'error':
        isRunning.value = false
        error.value = event.error
        cleanup()
        break

      case 'log':
        // 处理日志事件，显示stderr输出
        console.log('[Sidecar]', event.message)
        // 如果当前是"准备中"状态，尝试从日志中提取更详细的信息
        if (stage.value === '准备中...') {
          const message = event.message
          if (message.includes('步骤 1/3')) {
            stage.value = '初始化缓存目录...'
          } else if (message.includes('步骤 2/3')) {
            stage.value = '加载ONNX模型（可能需要下载，请耐心等待）...'
          } else if (message.includes('步骤 3/3')) {
            stage.value = '初始化完成'
          }
        }
        break
    }
  }

  // 处理翻译结果
  function processResult(result: {
    monoPdfPath?: string | null
    dualPdfPath?: string | null
    noWatermarkMonoPdfPath?: string | null
    noWatermarkDualPdfPath?: string | null
  }): void {
    if (result.monoPdfPath) {
      resultFiles.value.push({
        name: result.monoPdfPath.split('/').pop() || 'mono.pdf',
        path: result.monoPdfPath,
        type: '单语 PDF',
      })
    }
    if (result.dualPdfPath) {
      resultFiles.value.push({
        name: result.dualPdfPath.split('/').pop() || 'dual.pdf',
        path: result.dualPdfPath,
        type: '双语 PDF',
      })
    }
    if (result.noWatermarkMonoPdfPath) {
      resultFiles.value.push({
        name: result.noWatermarkMonoPdfPath.split('/').pop() || 'mono-nowm.pdf',
        path: result.noWatermarkMonoPdfPath,
        type: '单语 PDF',
      })
    }
    if (result.noWatermarkDualPdfPath) {
      resultFiles.value.push({
        name: result.noWatermarkDualPdfPath.split('/').pop() || 'dual-nowm.pdf',
        path: result.noWatermarkDualPdfPath,
        type: '双语 PDF',
      })
    }
  }

  // 清理监听器
  function cleanup(): void {
    if (unlistenFn) {
      unlistenFn()
      unlistenFn = null
    }
    currentTaskId = null
  }

  // 开始翻译
  async function startTranslation(config: TranslationConfig): Promise<void> {
    isRunning.value = true
    progress.value = 0
    stage.value = '准备中...'
    stageCurrent.value = 0
    stageTotal.value = 0
    error.value = null
    resultFiles.value = []
    currentFile.value = config.inputFile

    try {
      // 转换配置字段名（camelCase -> snake_case）
      const backendConfig = {
        input_file: config.inputFile,
        lang_in: config.langIn,
        lang_out: config.langOut,
        model: config.model,
        api_key: config.apiKey,
        base_url: config.baseUrl,
        pages: config.pages,
        output_dir: config.outputDir,
        output_dual: config.outputDual,
        output_mono: config.outputMono,
        watermark_mode: config.watermarkMode,
        enhance_compatibility: config.enhanceCompatibility,
        skip_clean: config.skipClean,
        qps: config.qps,
        auto_extract_glossary: config.autoExtractGlossary,
        ignore_cache: config.ignoreCache,
        enable_json_mode: config.enableJsonMode,
        send_dashscope_header: config.sendDashscopeHeader,
        no_send_temperature: config.noSendTemperature,
      }

      // 启动翻译
      const taskId = await invoke<string>('start_translation', {
        config: backendConfig,
      })
      currentTaskId = taskId

      // 监听事件
      unlistenFn = await listen<TranslationEvent>(
        `translation-event-${taskId}`,
        (event) => {
          handleEvent(event.payload)
        }
      )
    } catch (e) {
      error.value = String(e)
      isRunning.value = false
    }
  }

  // 取消翻译
  async function cancelTranslation(): Promise<void> {
    if (currentTaskId) {
      try {
        await invoke('cancel_translation', { taskId: currentTaskId })
      } catch (e) {
        console.error('Failed to cancel translation:', e)
      }
    }
    isRunning.value = false
    error.value = '翻译已取消'
    cleanup()
  }

  // 重置状态
  function reset(): void {
    isRunning.value = false
    progress.value = 0
    stage.value = ''
    stageCurrent.value = 0
    stageTotal.value = 0
    currentFile.value = null
    error.value = null
    resultFiles.value = []
    cleanup()
  }

  return {
    // 状态
    isRunning,
    progress,
    stage,
    stageCurrent,
    stageTotal,
    currentFile,
    error,
    resultFiles,
    uploadedFiles,
    // 计算属性
    hasFiles,
    hasResults,
    progressPercent,
    // 方法
    addFile,
    removeFile,
    clearFiles,
    startTranslation,
    cancelTranslation,
    reset,
  }
})
