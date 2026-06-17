import client from './client'

export interface DetectRequest {
  content: string
  detection_type?: 'phishing' | 'weak_password' | 'sensitive_info'
}

export interface DetectionResult {
  type: string
  risk_level: 'high' | 'medium' | 'low' | 'safe'
  confidence: number
  details: Record<string, unknown>
  suggestions: string[]
}

export interface DetectResponse {
  success: boolean
  result?: DetectionResult
  results?: Record<string, DetectionResult>
}

export async function detectText(data: DetectRequest): Promise<DetectResponse> {
  const response = await client.post<DetectResponse>('/api/detect/text', data)
  return response.data
}
