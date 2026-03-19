import apiClient from './client'
import type {
  LoginCredentials,
  Token,
  User,
  UserCreate,
  Guide,
  GuideCreate,
  PageAnalysisRequest,
  PageAnalysisResponse,
  ScreenshotAnalysisRequest,
  ScreenshotAnalysisResponse,
  CodeGenerationRequest,
  CodeGenerationResponse,
  PreviewData
} from '@/types'

// 认证 API
export const authApi = {
  login: (credentials: LoginCredentials) =>
    apiClient.post<Token>('/auth/login', credentials, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),

  register: (userData: UserCreate) =>
    apiClient.post<User>('/auth/register', userData),

  getCurrentUser: () =>
    apiClient.get<User>('/auth/me')
}

// 用户 API
export const userApi = {
  getUsers: (skip = 0, limit = 100) =>
    apiClient.get<User[]>('/users', { params: { skip, limit } }),

  getUser: (userId: number) =>
    apiClient.get<User>(`/users/${userId}`),

  updateUser: (userId: number, userData: Partial<User>) =>
    apiClient.put<User>(`/users/${userId}`, userData)
}

// 引导配置 API
export const guideApi = {
  createGuide: (guideData: GuideCreate) =>
    apiClient.post<Guide>('/guides/', guideData),

  getGuides: (skip = 0, limit = 100) =>
    apiClient.get<Guide[]>('/guides/', { params: { skip, limit } }),

  getGuide: (guideId: number) =>
    apiClient.get<Guide>(`/guides/${guideId}`),

  updateGuide: (guideId: number, guideData: Partial<Guide>) =>
    apiClient.put<Guide>(`/guides/${guideId}`, guideData),

  deleteGuide: (guideId: number) =>
    apiClient.delete(`/guides/${guideId}`)
}

// 页面分析 API (V1)
export const pageApi = {
  analyzePage: (request: PageAnalysisRequest) =>
    apiClient.post<PageAnalysisResponse>('/pages/analyze', request),

  generateCode: (request: CodeGenerationRequest) =>
    apiClient.post<CodeGenerationResponse>('/pages/generate-code', request),

  previewGuide: (guideId: number) =>
    apiClient.get<PreviewData>(`/pages/preview/${guideId}`)
}

// V2: 截图分析 API
export const screenshotApi = {
  analyzeWithScreenshot: (request: ScreenshotAnalysisRequest) =>
    apiClient.post<ScreenshotAnalysisResponse>('/v2/screenshot/analyze', request),

  getGuideScreenshots: (guideId: number) =>
    apiClient.get(`/v2/screenshot/guide/${guideId}`),

  getScreenshotImage: (screenshotId: number) =>
    apiClient.get(`/v2/screenshot/image/${screenshotId}`)
}
