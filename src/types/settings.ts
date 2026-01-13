// 模型配置
export interface ModelConfig {
  id: string
  displayName: string
  modelName: string
  apiKey: string
  baseUrl?: string | null
  enableJsonMode: boolean
  sendDashscopeHeader: boolean
  noSendTemperature: boolean
}

// 服务商
export interface Provider {
  id: string
  name: string
  defaultBaseUrl: string
  isBuiltin: boolean
  icon: string
  models: ModelConfig[]
}

// 服务商设置
export interface ProviderSettings {
  providers: Provider[]
  selectedModelId: string
}

// 术语提取设置
export interface TermExtractionSettings {
  useSeparateConfig: boolean
  modelConfigId: string
  customApiKey: string
  customBaseUrl: string
  customModel: string
  reasoning: string
}

// 翻译设置
export interface TranslationSettings {
  langIn: string
  langOut: string
  qps: number
  minTextLength: number
  poolMaxWorkers?: number | null
  termPoolMaxWorkers?: number | null
  customSystemPrompt: string
  autoExtractGlossary: boolean
  disableSameTextFallback: boolean
  addFormulaPlaceholdHint: boolean
  ignoreCache: boolean
  saveAutoExtractedGlossary: boolean
}

// PDF 设置
export interface PDFSettings {
  outputDual: boolean
  outputMono: boolean
  watermarkMode: 'watermarked' | 'no_watermark' | 'both'
  skipClean: boolean
  dualTranslateFirst: boolean
  disableRichTextTranslate: boolean
  enhanceCompatibility: boolean
  useAlternatingPagesDual: boolean
  maxPagesPerPart?: number | null
  skipScannedDetection: boolean
  ocrWorkaround: boolean
  autoEnableOcrWorkaround: boolean
  splitShortLines: boolean
  shortLineSplitFactor: number
  primaryFontFamily?: 'serif' | 'sans-serif' | 'script' | null
  formularFontPattern: string
  formularCharPattern: string
  skipFormRender: boolean
  skipCurveRender: boolean
  onlyParseGeneratePdf: boolean
  removeNonFormulaLines: boolean
  nonFormulaLineIouThreshold: number
  figureTableProtectionThreshold: number
  translateTableText: boolean
  onlyIncludeTranslatedPage: boolean
  mergeAlternatingLineNumbers: boolean
}

// RPC 设置
export interface RPCSettings {
  doclayoutHost: string
}

// 路径设置
export interface PathSettings {
  outputDir: string
  workingDir: string
  glossaryFiles: string
}

// 完整设置
export interface Settings {
  providers: ProviderSettings
  termExtraction: TermExtractionSettings
  translation: TranslationSettings
  pdf: PDFSettings
  rpc: RPCSettings
  paths: PathSettings
}

// 内置服务商预设
export const BUILTIN_PROVIDERS: Omit<Provider, 'models'>[] = [
  {
    id: 'openai',
    name: 'OpenAI',
    defaultBaseUrl: 'https://api.openai.com/v1',
    isBuiltin: true,
    icon: 'auto_awesome',
  },
  {
    id: 'deepseek',
    name: 'DeepSeek',
    defaultBaseUrl: 'https://api.deepseek.com',
    isBuiltin: true,
    icon: 'explore',
  },
  {
    id: 'zhipu',
    name: '智谱 GLM',
    defaultBaseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    isBuiltin: true,
    icon: 'psychology',
  },
  {
    id: 'ollama',
    name: 'Ollama (本地)',
    defaultBaseUrl: 'http://localhost:11434/v1',
    isBuiltin: true,
    icon: 'computer',
  },
  {
    id: 'claude',
    name: 'Claude (Anthropic)',
    defaultBaseUrl: 'https://api.anthropic.com/v1',
    isBuiltin: true,
    icon: 'chat',
  },
]

// 语言选项
export const LANGUAGE_OPTIONS = [
  { value: 'zh', label: '中文' },
  { value: 'en', label: 'English' },
  { value: 'ja', label: '日本語' },
  { value: 'ko', label: '한국어' },
  { value: 'fr', label: 'Français' },
  { value: 'de', label: 'Deutsch' },
  { value: 'es', label: 'Español' },
  { value: 'pt', label: 'Português' },
  { value: 'ru', label: 'Русский' },
  { value: 'ar', label: 'العربية' },
  { value: 'it', label: 'Italiano' },
]

// 默认设置
export function createDefaultSettings(): Settings {
  const defaultProviders: Provider[] = BUILTIN_PROVIDERS.map((p) => ({
    ...p,
    models: [],
  }))

  return {
    providers: {
      providers: defaultProviders,
      selectedModelId: '',
    },
    termExtraction: {
      useSeparateConfig: false,
      modelConfigId: '',
      customApiKey: '',
      customBaseUrl: '',
      customModel: '',
      reasoning: '',
    },
    translation: {
      langIn: 'en',
      langOut: 'zh',
      qps: 4,
      minTextLength: 5,
      poolMaxWorkers: null,
      termPoolMaxWorkers: null,
      customSystemPrompt: '',
      autoExtractGlossary: true,
      disableSameTextFallback: false,
      addFormulaPlaceholdHint: false,
      ignoreCache: false,
      saveAutoExtractedGlossary: false,
    },
    pdf: {
      outputDual: true,
      outputMono: true,
      watermarkMode: 'watermarked',
      skipClean: false,
      dualTranslateFirst: false,
      disableRichTextTranslate: false,
      enhanceCompatibility: false,
      useAlternatingPagesDual: false,
      maxPagesPerPart: null,
      skipScannedDetection: false,
      ocrWorkaround: false,
      autoEnableOcrWorkaround: false,
      splitShortLines: false,
      shortLineSplitFactor: 0.8,
      primaryFontFamily: null,
      formularFontPattern: '',
      formularCharPattern: '',
      skipFormRender: false,
      skipCurveRender: false,
      onlyParseGeneratePdf: false,
      removeNonFormulaLines: false,
      nonFormulaLineIouThreshold: 0.9,
      figureTableProtectionThreshold: 0.9,
      translateTableText: false,
      onlyIncludeTranslatedPage: false,
      mergeAlternatingLineNumbers: false,
    },
    rpc: {
      doclayoutHost: '',
    },
    paths: {
      outputDir: '',
      workingDir: '',
      glossaryFiles: '',
    },
  }
}
