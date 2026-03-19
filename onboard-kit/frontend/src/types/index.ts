// 用户相关类型
export interface User {
  id: number
  email: string
  full_name?: string
  company?: string
  is_active: boolean
  is_trial: boolean
  trial_expires_at?: string
  created_at: string
}

export interface UserCreate {
  email: string
  password: string
  full_name?: string
  company?: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

// V2: 截图区域类型
export interface ScreenshotRegion {
  x: number
  y: number
  width: number
  height: number
  element_type: string
  selector: string
  title: string
  confidence: number
  is_added?: boolean
}

// V2: 截图分析响应
export interface ScreenshotAnalysisResponse {
  screenshot: string // base64 data URL
  width: number
  height: number
  suggested_regions: ScreenshotRegion[]
  url: string
}

// 引导配置相关类型
export interface Step {
  id?: number
  guide_id?: number
  order: number
  title: string
  description?: string
  element_selector: string
  position: 'top' | 'bottom' | 'left' | 'right'
  config?: Record<string, any>
  // V2: 截图坐标支持
  screenshot_region?: {
    x: number
    y: number
    width: number
    height: number
  }
  is_manual_selection?: boolean
  created_at?: string
}

export interface Guide {
  id?: number
  name: string
  description?: string
  target_url: string
  config?: Record<string, any>
  is_published?: boolean
  owner_id?: number
  created_at?: string
  updated_at?: string
  steps: Step[]
}

export interface GuideCreate {
  name: string
  description?: string
  target_url: string
  config?: Record<string, any>
  steps?: Omit<Step, 'id' | 'guide_id' | 'created_at'>[]
}

// 页面分析相关类型 (V1)
export interface PageAnalysisRequest {
  url: string
}

export interface SuggestedElement {
  type: string
  selector: string
  title: string
  description: string
  priority: number
}

export interface PageAnalysisResponse {
  id: number
  url: string
  analysis_result: {
    title: string
    forms: any[]
    buttons: any[]
    inputs: any[]
    sections: any[]
  }
  suggested_elements?: SuggestedElement[]
  created_at: string
}

// V2: 截图分析请求
export interface ScreenshotAnalysisRequest {
  url: string
  guide_id?: number
}

// 代码生成相关类型
export interface CodeGenerationRequest {
  guide_id: number
  format: 'html' | 'js' | 'npm'
}

export interface CodeGenerationResponse {
  code: string
  format: string
  instructions: string
}

// Driver.js 配置类型
export interface DriverStep {
  element: string
  popover: {
    title: string
    description: string
    side: 'top' | 'bottom' | 'left' | 'right'
  }
}

export interface PreviewData {
  guide: {
    id: number
    name: string
    target_url: string
  }
  steps: DriverStep[]
  config: Record<string, any>
}
