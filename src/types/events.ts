// 进度更新事件
export interface ProgressUpdateEvent {
  type: 'progress_update'
  stage: string
  stageCurrent: number
  stageTotal: number
  overallProgress: number
}

// 完成事件
export interface FinishEvent {
  type: 'finish'
  translateResult: TranslateResult
}

// 错误事件
export interface ErrorEvent {
  type: 'error'
  error: string
}

// 日志事件
export interface LogEvent {
  type: 'log'
  message: string
}

// 翻译结果
export interface TranslateResult {
  originalPdfPath: string
  totalSeconds: number
  monoPdfPath?: string | null
  dualPdfPath?: string | null
  noWatermarkMonoPdfPath?: string | null
  noWatermarkDualPdfPath?: string | null
  peakMemoryUsage?: number | null
  autoExtractedGlossaryPath?: string | null
}

// 联合事件类型
export type TranslationEvent = ProgressUpdateEvent | FinishEvent | ErrorEvent | LogEvent

// 上传的文件
export interface UploadedFile {
  id: string
  name: string
  path: string
  size: number
}

// 结果文件
export interface ResultFile {
  name: string
  path: string
  type: '单语 PDF' | '双语 PDF'
}

// 翻译配置（发送给后端）
export interface TranslationConfig {
  inputFile: string
  langIn: string
  langOut: string
  model: string
  apiKey: string
  baseUrl?: string
  pages?: string
  outputDir?: string
  outputDual: boolean
  outputMono: boolean
  watermarkMode?: string
  enhanceCompatibility?: boolean
  skipClean?: boolean
  qps?: number
  autoExtractGlossary?: boolean
  ignoreCache?: boolean
  enableJsonMode?: boolean
  sendDashscopeHeader?: boolean
  noSendTemperature?: boolean
}
