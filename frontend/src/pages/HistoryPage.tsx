import { useEffect, useMemo, useState } from 'react'
import { useHistoryStore } from '../store/useStore'

const RISK_BADGES: Record<string, string> = {
  high: 'bg-rose-50 text-rose-700 ring-rose-200',
  medium: 'bg-amber-50 text-amber-700 ring-amber-200',
  low: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  safe: 'bg-sky-50 text-sky-700 ring-sky-200',
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
  }, [fetchHistory])

  const totalPages = useMemo(() => Math.ceil(historyTotal / historyPageSize), [historyTotal, historyPageSize])
  const emptyState = !loading && historyList.length === 0

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
    <div className="mx-auto max-w-6xl">
      <div className="rounded-[28px] border border-white/70 bg-white/80 p-6 shadow-xl shadow-slate-200/40 backdrop-blur-xl">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <span className="inline-flex rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold tracking-wide text-white">
              历史记录
            </span>
            <h2 className="mt-3 text-3xl font-bold text-slate-900">检测历史</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
              查看最近的检测记录、分页浏览、删除单条记录或一键清空全部历史。
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-700">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">总记录</p>
              <p className="mt-1 text-lg font-bold text-slate-900">{historyTotal}</p>
            </div>
            {historyList.length > 0 && (
              <button
                onClick={handleClear}
                onBlur={() => setConfirmClear(false)}
                className={`rounded-2xl px-4 py-3 text-sm font-semibold transition-all ${
                  confirmClear
                    ? 'bg-rose-600 text-white shadow-lg shadow-rose-200 hover:bg-rose-700'
                    : 'border border-rose-200 bg-white text-rose-600 hover:bg-rose-50'
                }`}
              >
                {confirmClear ? '再次点击确认清空' : '清空所有'}
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        )}

        <div className="mt-6">
          {loading && historyList.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 py-12 text-center text-slate-500">
              正在加载历史记录...
            </div>
          ) : emptyState ? (
            <div className="rounded-2xl border border-dashed border-slate-200 bg-white py-14 text-center shadow-sm">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-2xl">🗂️</div>
              <p className="mt-4 text-lg font-semibold text-slate-900">暂无检测记录</p>
              <p className="mt-2 text-sm text-slate-500">完成一次检测后，结果会自动保存到这里。</p>
            </div>
          ) : (
            <>
              <div className="space-y-3">
                {historyList.map((item) => (
                  <div
                    key={item.id}
                    className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md md:flex-row md:items-center md:justify-between"
                  >
                    <div className="flex flex-wrap items-center gap-3">
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ring-1 ${RISK_BADGES[item.risk_level] || RISK_BADGES.safe}`}
                      >
                        {RISK_LABELS[item.risk_level] || item.risk_level}
                      </span>
                      <div>
                        <p className="text-sm font-semibold text-slate-900">
                          {TYPE_LABELS[item.detection_type] || item.detection_type}
                        </p>
                        <p className="text-xs text-slate-500">{new Date(item.created_at).toLocaleString('zh-CN')}</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between gap-3 md:justify-end">
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                        记录 #{item.id}
                      </span>
                      <button
                        onClick={() => deleteHistoryItem(item.id)}
                        className="rounded-xl px-3 py-2 text-sm font-semibold text-slate-500 transition hover:bg-slate-100 hover:text-rose-600"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 flex items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                <p className="text-sm text-slate-600">
                  第 <span className="font-semibold text-slate-900">{historyPage}</span> /{' '}
                  <span className="font-semibold text-slate-900">{totalPages || 1}</span> 页
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handlePageChange(historyPage - 1)}
                    disabled={historyPage <= 1}
                    className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    上一页
                  </button>
                  <button
                    onClick={() => handlePageChange(historyPage + 1)}
                    disabled={historyPage >= totalPages}
                    className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    下一页
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
