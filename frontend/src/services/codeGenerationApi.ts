/**
 * Code Generation API Service - Green段階（テストを通すための実装）
 * コード生成API通信サービス
 */

export interface GenerationRequest {
  user_prompt: string
  complexity: string
  include_security: boolean
  include_accessibility: boolean
  target_framework: string
  max_files: number
  timeout: number
}

export interface GeneratedFile {
  filename: string
  content: string
  language: string
  description?: string
}

export interface GenerationResponse {
  success: boolean
  generated_files: GeneratedFile[]
  errors: string[]
  warnings: string[]
  performance_metrics: Record<string, any>
}

export interface ValidationRequest {
  code_blocks: Array<{
    filename: string
    content: string
    language: string
    description?: string
  }>
}

export interface ValidationError {
  message: string
  line: number
  column: number
}

export interface SecurityRisk {
  type: string
  severity: string
  description: string
  line?: number
}

export interface ValidationResult {
  filename: string
  is_valid: boolean
  syntax_errors: ValidationError[]
  type_errors: ValidationError[]
  lint_errors: ValidationError[]
  security_risks: SecurityRisk[]
}

export interface ValidationResponse {
  is_valid: boolean
  validation_results: ValidationResult[]
  security_risks: SecurityRisk[]
}

export interface Template {
  name: string
  description: string
  complexity_levels: string[]
}

export interface TemplatesResponse {
  templates: Template[]
}

export interface TemplateDetail {
  name: string
  description: string
  base_prompt: string
  complexity_adjustments: Record<string, string>
}

export interface ApiError extends Error {
  status?: number
  code?: string
}

// API設定
const API_BASE_URL = 'http://localhost:8000/api'
const API_TIMEOUT = 30000 // 30秒

class CodeGenerationApiService {
  private createApiError(message: string, status?: number, code?: string): ApiError {
    const error = new Error(message) as ApiError
    error.status = status
    error.code = code
    return error
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT)

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
        ...options,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`
        
        try {
          const errorData = await response.json()
          if (errorData.detail) {
            errorMessage = errorData.detail
          }
        } catch {
          // JSON パースエラーは無視
        }

        throw this.createApiError(errorMessage, response.status)
      }

      const data = await response.json()
      return data
    } catch (error) {
      clearTimeout(timeoutId)
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw this.createApiError('リクエストがタイムアウトしました', undefined, 'TIMEOUT')
        }
        
        if ((error as ApiError).status) {
          throw error // API エラーはそのまま再投げ
        }
      }

      // ネットワークエラーなど
      throw this.createApiError('ネットワークエラーが発生しました', undefined, 'NETWORK_ERROR')
    }
  }

  async generateCode(request: GenerationRequest): Promise<GenerationResponse> {
    return this.request<GenerationResponse>('/code-generation/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async validateCode(request: ValidationRequest): Promise<ValidationResponse> {
    return this.request<ValidationResponse>('/code-generation/validate', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getTemplates(): Promise<TemplatesResponse> {
    return this.request<TemplatesResponse>('/code-generation/templates')
  }

  async getTemplateDetail(templateName: string): Promise<TemplateDetail> {
    return this.request<TemplateDetail>(`/code-generation/templates/${encodeURIComponent(templateName)}`)
  }

  async getHealth(): Promise<Record<string, any>> {
    return this.request<Record<string, any>>('/code-generation/health')
  }

  async getCacheStats(): Promise<Record<string, any>> {
    return this.request<Record<string, any>>('/code-generation/cache/stats')
  }

  async clearCache(): Promise<{ message: string; timestamp: number }> {
    return this.request<{ message: string; timestamp: number }>('/code-generation/cache', {
      method: 'DELETE',
    })
  }
}

// シングルトンインスタンス
const apiService = new CodeGenerationApiService()

// 便利な関数としてエクスポート
export const generateCode = (request: GenerationRequest) => apiService.generateCode(request)
export const validateCode = (request: ValidationRequest) => apiService.validateCode(request)
export const getTemplates = () => apiService.getTemplates()
export const getTemplateDetail = (templateName: string) => apiService.getTemplateDetail(templateName)
export const getHealth = () => apiService.getHealth()
export const getCacheStats = () => apiService.getCacheStats()
export const clearCache = () => apiService.clearCache()

export { apiService as codeGenerationApi }