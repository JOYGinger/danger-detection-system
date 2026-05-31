import { useEffect, useState } from 'react'
import { useHistoryStore } from '../store/useStore'

const RISK_COLORS: Record<string, string> = {
  high: 'bg-red-100 text-red-800',
  medium: 'bg-orange-100 text-orange-800',
  low: 'bg-green-100 text-green-800',
  safe: 'bg-blue-100 text-blue-800',
}

const RISK_LABELS: Record<string, string> = {
  high: '高风险',
  medium: '中风险',
  low: '低风险',
  safe: '安全',
}

const TYPE_LABELS: Record<string, string> = {
  sensitive_info: '敏感信息',
  weak_password: '弱密码',
  phishing: '钓鱼邮件',
  all: '全部',
}

export default function HistoryPage() {
  const {
    historyList,
    historyTotal,
    historyPage,
    historyPageSize,
    loading,
    error,
    fetchHistory,
    deleteHistoryItem,
    clearAllHistory,
  } = useHistoryStore()

  const [confirmClear, setConfirmClear] = useState(false)

  useEffect(() => {
    fetchHistory()
  }, [])

  const totalPages = Math.ceil(historyTotal / historyPageSize)

  const handlePageChange = (page: number) => {
    fetchHistory(page, historyPageSize)
  }

  const handleClear = async () => {
    if (!confirmClear) {
      setConfirmClear(true)
      return
    }
    await clearAllHistory()
    setConfirmClear(false)
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">检测历史</h2>
        {historyList.length > 0 && (
          <button
            onClick={handleClear}
            onBlur={() => setConfirmClear(false)}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              confirmClear
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'border border-red-300 text-red-600 hover:bg-red-50'
            }`}
          >
            {confirmClear ? '确认清空？' : '清空所有'}
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-4">
          {error}
        </div>
      )}

      {loading && historyList.length === 0 ? (
        <div className="text-center text-gray-500 py-8">加载中...</div>
      ) : historyList.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
          暂无检测记录
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {historyList.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-lg shadow-md p-4 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <span className={`text-xs px-2 py-1 rounded font-medium ${RISK_COLORS[item.risk_level]}`}>
                    {RISK_LABELS[item.risk_level] || item.risk_level}
                  </span>
                  <div>
                    <span className="text-sm text-gray-700">
                      {TYPE_LABELS[item.detection_type] || item.detection_type}
                    </span>
                    <span className="text-xs text-gray-400 ml-3">
                      {new Date(item.created_at).toLocaleString('zh-CN')}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => deleteHistoryItem(item.id)}
                  className="text-sm text-gray-400 hover:text-red-500 transition-colors"
                >
                  删除
                </button>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <button
                onClick={() => handlePageChange(historyPage - 1)}
                disabled={historyPage <= 1}
                className="px-3 py-1 border rounded text-sm disabled:opacity-50 hover:bg-gray-50"
              >
                上一页
              </button>
              <span className="text-sm text-gray-600">
                第 {historyPage} / {totalPages} 页
              </span>
              <button
                onClick={() => handlePageChange(historyPage + 1)}
                disabled={historyPage >= totalPages}
                className="px-3 py-1 border rounded text-sm disabled:opacity-50 hover:bg-gray-50"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
