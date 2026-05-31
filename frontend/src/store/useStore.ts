import { create } from 'zustand'
import {
  detectText as apiDetectText,
  type DetectResponse,
  type DetectionResult,
} from '../api/detection'
import {
  getHistory as apiGetHistory,
  getHistoryDetail as apiGetHistoryDetail,
  deleteHistoryItem as apiDeleteHistoryItem,
  clearHistory as apiClearHistory,
  type HistoryItem,
  type HistoryDetail,
} from '../api/history'

interface DetectionState {
  currentResult: DetectResponse | null
  loading: boolean
  error: string | null
  detectText: (content: string, detectionType?: 'phishing' | 'weak_password' | 'sensitive_info') => Promise<void>
  clearResult: () => void
}

interface HistoryState {
  historyList: HistoryItem[]
  historyDetail: HistoryDetail | null
  historyTotal: number
  historyPage: number
  historyPageSize: number
  loading: boolean
  error: string | null
  fetchHistory: (page?: number, pageSize?: number) => Promise<void>
  fetchHistoryDetail: (id: number) => Promise<void>
  deleteHistoryItem: (id: number) => Promise<void>
  clearAllHistory: () => Promise<void>
}

export const useDetectionStore = create<DetectionState>((set) => ({
  currentResult: null,
  loading: false,
  error: null,
  detectText: async (content, detectionType) => {
    set({ loading: true, error: null })
    try {
      const result = await apiDetectText({ content, detection_type: detectionType })
      set({ currentResult: result, loading: false })
    } catch (e) {
      set({ error: (e as Error).message, loading: false })
    }
  },
  clearResult: () => set({ currentResult: null, error: null }),
}))

export const useHistoryStore = create<HistoryState>((set, get) => ({
  historyList: [],
  historyDetail: null,
  historyTotal: 0,
  historyPage: 1,
  historyPageSize: 10,
  loading: false,
  error: null,
  fetchHistory: async (page = 1, pageSize = 10) => {
    set({ loading: true, error: null })
    try {
      const data = await apiGetHistory(page, pageSize)
      set({
        historyList: data.items,
        historyTotal: data.total,
        historyPage: data.page,
        historyPageSize: data.page_size,
        loading: false,
      })
    } catch (e) {
      set({ error: (e as Error).message, loading: false })
    }
  },
  fetchHistoryDetail: async (id) => {
    set({ loading: true, error: null })
    try {
      const detail = await apiGetHistoryDetail(id)
      set({ historyDetail: detail, loading: false })
    } catch (e) {
      set({ error: (e as Error).message, loading: false })
    }
  },
  deleteHistoryItem: async (id) => {
    try {
      await apiDeleteHistoryItem(id)
      const { historyPage, historyPageSize } = get()
      const data = await apiGetHistory(historyPage, historyPageSize)
      set({
        historyList: data.items,
        historyTotal: data.total,
      })
    } catch (e) {
      set({ error: (e as Error).message })
    }
  },
  clearAllHistory: async () => {
    try {
      await apiClearHistory()
      set({ historyList: [], historyTotal: 0, historyDetail: null })
    } catch (e) {
      set({ error: (e as Error).message })
    }
  },
}))
