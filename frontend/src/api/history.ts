import client from './client'

export interface HistoryItem {
  id: number
  detection_type: string
  risk_level: string
  created_at: string
}

export interface HistoryList {
  items: HistoryItem[]
  total: number
  page: number
  page_size: number
}

export interface HistoryDetail {
  id: number
  input_content: string
  detection_type: string
  risk_level: string
  result_detail: Record<string, unknown>
  created_at: string
}

export async function getHistory(
  page: number = 1,
  pageSize: number = 10
): Promise<HistoryList> {
  const response = await client.get<HistoryList>('/api/history', {
    params: { page, page_size: pageSize },
  })
  return response.data
}

export async function getHistoryDetail(id: number): Promise<HistoryDetail> {
  const response = await client.get<HistoryDetail>(`/api/history/${id}`)
  return response.data
}

export async function deleteHistoryItem(id: number): Promise<void> {
  await client.delete(`/api/history/${id}`)
}

export async function clearHistory(): Promise<{ deleted_count: number }> {
  const response = await client.delete('/api/history')
  return response.data
}
