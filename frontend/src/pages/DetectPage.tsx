import { useMemo, useState } from 'react'
import { useDetectionStore } from '../store/useStore'
import type { DetectionResult } from '../api/detection'

const DETECTION_TYPES = [
  { value: '', label: '全部检测', hint: '一次性扫描多类风险' },
  { value: 'sensitive_info', label: '敏感信息检测', hint: '识别密钥、邮箱、手机号等' },
  { value: 'weak_password', label: '弱密码检测', hint: '评估密码强度与可破解性' },
  { value: 'phishing', label: '钓鱼邮件检测', hint: '识别社工、短链与伪装特征' },
] as const

const RISK_STYLES: Record<string, string> = {
  high: 'from-rose-500/20 to-rose-500/5 border-rose-200 text-rose-900',
  medium: 'from-amber-500/20 to-amber-500/5 border-amber-200 text-amber-900',
  low: 'from-emerald-500/20 to-emerald-500/5 border-emerald-200 text-emerald-900',
  safe: 'from-sky-500/20 to-sky-500/5 border-sky-200 text-sky-900',
}

const RISK_LABELS: Record<string, string> = {
  high: '高风险',
  medium: '中风险',
  low: '低风险',
  safe: '安全',
}

const TYPE_LABELS: Record<string, string> = {
  sensitive_info: '敏感信息检测',
  weak_password: '弱密码检测',
  phishing: '钓鱼邮件检测',
}

function ResultCard({ result }: { result: DetectionResult }) {
  const riskClass = RISK_STYLES[result.risk_level] || RISK_STYLES.safe
  const findings = Array.isArray(result.details?.findings) ? result.details.findings : []
  const detailsCount = result.details?.count as number | undefined
  const riskLabel = RISK_LABELS[result.risk_level] || result.risk_level

  return (
    <div className={`rounded-2xl border bg-gradient-to-br p-5 shadow-sm backdrop-blur ${riskClass}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">检测结果</p>
          <h3 className="mt-1 text-lg font-bold text-slate-900">{TYPE_LABELS[result.type] || result.type}</h3>
          <p className="mt-1 text-sm text-slate-600">置信度 {Math.round(result.confidence * 100)}%</p>
        </div>
        <span className="inline-flex items-center rounded-full bg-white/80 px-3 py-1 text-sm font-semibold shadow-sm ring-1 ring-black/5">
          {riskLabel}
        </span>
      </div>

      {result.details && Object.keys(result.details).length > 0 && (
        <div className="mt-4 grid gap-3 rounded-xl bg-white/70 p-4 text-sm text-slate-700 ring-1 ring-black/5">
          <div className="grid gap-2 sm:grid-cols-2">
            {typeof detailsCount === 'number' && (
              <div className="rounded-lg bg-slate-50 px-3 py-2">
                <p className="text-xs text-slate-500">发现项</p>
                <p className="font-semibold text-slate-900">{detailsCount} 项</p>
              </div>
            )}
            {typeof result.details.score === 'number' && (
              <div className="rounded-lg bg-slate-50 px-3 py-2">
                <p className="text-xs text-slate-500">评分</p>
                <p className="font-semibold text-slate-900">{result.details.score}</p>
              </div>
            )}
            {result.details.crack_time && (
              <div className="rounded-lg bg-slate-50 px-3 py-2">
                <p className="text-xs text-slate-500">破解时间</p>
                <p className="font-semibold text-slate-900">{result.details.crack_time as string}</p>
              </div>
            )}
            {typeof result.details.entropy === 'number' && (
              <div className="rounded-lg bg-slate-50 px-3 py-2">
                <p className="text-xs text-slate-500">熵值</p>
                <p className="font-semibold text-slate-900">{result.details.entropy}</p>
              </div>
            )}
          </div>

          {findings.length > 0 && (
            <div>
              <p className="font-semibold text-slate-900">详细发现</p>
              <ul className="mt-2 space-y-2">
                {findings.map((f: { type: string; masked_value?: string; risk?: string; keyword?: string }, i: number) => (
                  <li key={i} className="rounded-lg bg-slate-50 px-3 py-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-slate-900 px-2 py-0.5 text-xs font-medium text-white">{f.type}</span>
                      <span className="font-mono text-sm text-slate-700">{f.masked_value || f.keyword || '—'}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {result.suggestions.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-semibold text-slate-900">安全建议</p>
          <ul className="mt-2 space-y-2 text-sm text-slate-700">
            {result.suggestions.map((s, i) => (
              <li key={i} className="flex gap-2 rounded-lg bg-white/70 px-3 py-2 ring-1 ring-black/5">
                <span className="mt-1 h-2 w-2 flex-none rounded-full bg-current opacity-70" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default function DetectPage() {
  const [content, setContent] = useState('')
  const [detectionType, setDetectionType] = useState('')
  const { currentResult, loading, error, detectText, clearResult } = useDetectionStore()

  const selectedTypeMeta = useMemo(
    () => DETECTION_TYPES.find((item) => item.value === detectionType) || DETECTION_TYPES[0],
    [detectionType]
  )

  const handleDetect = () => {
    if (!content.trim()) return
    detectText(
      content,
      detectionType ? (detectionType as 'phishing' | 'weak_password' | 'sensitive_info') : undefined
    )
  }

  const handleClear = () => {
    setContent('')
    clearResult()
  }

  return (
    <div className="mx-auto max-w-6xl">
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="overflow-hidden rounded-[28px] border border-white/70 bg-white/80 p-6 shadow-xl shadow-slate-200/40 backdrop-blur-xl">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <span className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold tracking-wide text-blue-700">
                本地安全检测
              </span>
              <h2 className="mt-3 text-3xl font-bold text-slate-900">文本安全检测</h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                输入邮件、密码或文本内容，即可快速识别钓鱼、弱密码和敏感信息风险，所有检测在本地执行。
              </p>
            </div>
            <div className="rounded-2xl bg-slate-900 px-4 py-3 text-white shadow-lg shadow-slate-900/20">
              <p className="text-xs uppercase tracking-[0.25em] text-slate-300">当前模式</p>
              <p className="mt-1 text-sm font-semibold">{selectedTypeMeta.label}</p>
              <p className="mt-1 text-xs text-slate-300">{selectedTypeMeta.hint}</p>
            </div>
          </div>

          <div className="mt-6 grid gap-4">
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">检测类型</label>
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {DETECTION_TYPES.map((t) => {
                  const active = detectionType === t.value
                  return (
                    <button
                      key={t.value}
                      type="button"
                      onClick={() => setDetectionType(t.value)}
                      className={`rounded-2xl border px-4 py-3 text-left transition-all duration-200 ${
                        active
                          ? 'border-blue-500 bg-blue-50 text-blue-900 shadow-md shadow-blue-100'
                          : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'
                      }`}
                    >
                      <div className="font-semibold">{t.label}</div>
                      <div className="mt-1 text-xs leading-5 text-slate-500">{t.hint}</div>
                    </button>
                  )
                })}
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">检测内容</label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="请输入要检测的文本内容..."
                rows={8}
                className="w-full rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-slate-800 shadow-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 resize-y"
              />
              <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                <span>支持长文本粘贴与多类内容混合检测</span>
                <span>{content.length} 字符</span>
              </div>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <button
                onClick={handleDetect}
                disabled={loading || !content.trim()}
                className="inline-flex flex-1 items-center justify-center gap-2 rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />}
                {loading ? '检测中...' : '开始检测'}
              </button>
              <button
                onClick={handleClear}
                className="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
              >
                清空内容
              </button>
            </div>

            {error && (
              <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {error}
              </div>
            )}
          </div>
        </section>

        <aside className="space-y-6">
          <div className="rounded-[28px] border border-white/70 bg-white/80 p-6 shadow-xl shadow-slate-200/40 backdrop-blur-xl">
            <h3 className="text-lg font-bold text-slate-900">使用提示</h3>
            <ul className="mt-4 space-y-3 text-sm text-slate-600">
              <li className="rounded-2xl bg-slate-50 px-4 py-3">1. 先选择检测类型，再粘贴文本内容。</li>
              <li className="rounded-2xl bg-slate-50 px-4 py-3">2. 支持一次输入多种风险内容进行扫描。</li>
              <li className="rounded-2xl bg-slate-50 px-4 py-3">3. 检测结果会自动保存到历史记录中。</li>
            </ul>
          </div>

          <div className="rounded-[28px] border border-white/70 bg-gradient-to-br from-slate-900 to-slate-700 p-6 text-white shadow-xl shadow-slate-200/40">
            <p className="text-xs uppercase tracking-[0.25em] text-slate-300">当前状态</p>
            <p className="mt-2 text-2xl font-bold">{loading ? '正在分析' : '等待输入'}</p>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              若页面无结果，请检查内容是否为空，或切换到对应检测类型后重新提交。
            </p>
          </div>
        </aside>
      </div>

      {currentResult && currentResult.success && (
        <div className="mt-8 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-slate-900">检测结果</h3>
            <span className="text-sm text-slate-500">结果已自动保存到历史记录</span>
          </div>

          {currentResult.result && <ResultCard result={currentResult.result} />}

          {currentResult.results && (
            <div className="grid gap-4 xl:grid-cols-3">
              {Object.entries(currentResult.results).map(([key, result]) => (
                <ResultCard key={key} result={result} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
