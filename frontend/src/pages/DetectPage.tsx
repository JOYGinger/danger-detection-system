import { useState } from 'react'
import { useDetectionStore } from '../store/useStore'
import type { DetectionResult } from '../api/detection'

const DETECTION_TYPES = [
  { value: '', label: '全部检测' },
  { value: 'sensitive_info', label: '敏感信息检测' },
  { value: 'weak_password', label: '弱密码检测' },
  { value: 'phishing', label: '钓鱼邮件检测' },
] as const

const RISK_COLORS: Record<string, string> = {
  high: 'bg-red-100 text-red-800 border-red-300',
  medium: 'bg-orange-100 text-orange-800 border-orange-300',
  low: 'bg-green-100 text-green-800 border-green-300',
  safe: 'bg-blue-100 text-blue-800 border-blue-300',
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
  return (
    <div className={`rounded-lg border p-4 ${RISK_COLORS[result.risk_level]}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold">{TYPE_LABELS[result.type] || result.type}</h3>
        <span className="text-sm font-medium px-2 py-0.5 rounded">
          {RISK_LABELS[result.risk_level]}
        </span>
      </div>
      <p className="text-sm mb-2">置信度: {Math.round(result.confidence * 100)}%</p>

      {result.details && Object.keys(result.details).length > 0 && (
        <div className="mt-2 text-sm">
          <p className="font-medium mb-1">详细结果:</p>
          <ul className="list-disc list-inside space-y-0.5">
            {result.details.count !== undefined && (
              <li>发现 {result.details.count as number} 项敏感信息</li>
            )}
            {Array.isArray(result.details.findings) &&
              (result.details.findings as Array<{ type: string; masked_value: string; risk: string }>).map((f, i) => (
                <li key={i}>
                  [{RISK_LABELS[f.risk] || f.risk}] {f.masked_value}
                </li>
              ))}
          </ul>
        </div>
      )}

      {result.suggestions.length > 0 && (
        <div className="mt-2 text-sm">
          <p className="font-medium mb-1">安全建议:</p>
          <ul className="list-disc list-inside space-y-0.5">
            {result.suggestions.map((s, i) => (
              <li key={i}>{s}</li>
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

  const handleDetect = () => {
    if (!content.trim()) return
    detectText(
      content,
      detectionType ? (detectionType as 'phishing' | 'weak_password' | 'sensitive_info') : undefined
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">文本安全检测</h2>

      <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">检测类型</label>
          <select
            value={detectionType}
            onChange={(e) => setDetectionType(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {DETECTION_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">检测内容</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="请输入要检测的文本内容..."
            rows={6}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleDetect}
            disabled={loading || !content.trim()}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? '检测中...' : '开始检测'}
          </button>
          <button
            onClick={() => { setContent(''); clearResult() }}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-600 hover:bg-gray-50 transition-colors"
          >
            清空
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}
      </div>

      {currentResult && currentResult.success && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">检测结果</h3>

          {currentResult.result && (
            <ResultCard result={currentResult.result} />
          )}

          {currentResult.results && (
            <div className="space-y-3">
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
