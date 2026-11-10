import { useEffect, useState } from 'react'
import { callApi } from '../api'
import { todayIso } from '../format'

const year = new Date().getFullYear()

// Each example is a function of the chosen region, so switching region updates the URLs.
const EXAMPLES = [
  { label: 'Holidays this year', path: (r) => `/v1/regions/${r}/holidays?year=${year}` },
  { label: 'Next 3 holidays', path: (r) => `/v1/regions/${r}/holidays/next?count=3` },
  { label: 'Is today a business day?', path: (r) => `/v1/regions/${r}/dates/${todayIso()}` },
  { label: '10 business days from today', path: (r) => `/v1/regions/${r}/business-days/add?start=${todayIso()}&days=10` },
  { label: 'Search (paginated)', path: (r) => `/v1/holidays?year=${year}&region=${r}&per_page=3&page=2` },
  { label: 'An error', path: (r) => `/v1/regions/${r}/holidays?year=1999` },
]

const SNIPPETS = {
  curl: (url) => `curl -i "${url}"`,
  Python: (url) => `import httpx

response = httpx.get("${url}")
print(response.json())`,
  JavaScript: (url) => `const response = await fetch("${url}")
const data = await response.json()`,
}

export default function Playground({ region }) {
  const [example, setExample] = useState(0)
  const [path, setPath] = useState(EXAMPLES[0].path(region))
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [snippet, setSnippet] = useState('curl')

  const send = async (target = path) => {
    setBusy(true)
    try {
      setResult({ path: target, ...(await callApi(target)) })
    } catch (err) {
      setResult({ path: target, status: 0, error: err.message, headers: [] })
    } finally {
      setBusy(false)
    }
  }

  // Follow the region picker, and run the chosen example straight away.
  useEffect(() => {
    const next = EXAMPLES[example].path(region)
    setPath(next)
    send(next)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [region, example])

  const fullUrl = `${window.location.origin}${path}`
  return (
    <div className="playground card">
      <div className="examples" role="tablist" aria-label="Examples">
        {EXAMPLES.map((ex, i) => (
          <button key={ex.label} role="tab" aria-selected={i === example}
            className={`chip-button ${i === example ? 'on' : ''}`} onClick={() => setExample(i)}>
            {ex.label}
          </button>
        ))}
      </div>
      <form className="request-line" onSubmit={(e) => { e.preventDefault(); send() }}>
        <span className="method">GET</span>
        <input value={path} onChange={(e) => setPath(e.target.value)} aria-label="Request path" spellCheck="false" />
        <button className="button" disabled={busy}>{busy ? 'Sending…' : 'Send'}</button>
      </form>

      {result && (
        <div className="response" aria-live="polite">
          <div className="status-line">
            <span className={`status ${result.ok ? 'ok' : 'bad'}`}>{result.status || 'Network error'}</span>
            {result.ms !== undefined && <span className="muted small">{result.ms} ms</span>}
          </div>
          {result.headers.length > 0 && (
            <dl className="headers">
              {result.headers.map(([name, value]) => (
                <div key={name}><dt>{name}</dt><dd>{value}</dd></div>
              ))}
            </dl>
          )}
          <pre className="code json">{result.error || JSON.stringify(result.body, null, 2)}</pre>
        </div>
      )}

      <div className="snippets">
        <div className="row">
          {Object.keys(SNIPPETS).map((name) => (
            <button key={name} className={`tab-button ${snippet === name ? 'on' : ''}`}
              onClick={() => setSnippet(name)} aria-pressed={snippet === name}>{name}</button>
          ))}
        </div>
        <pre className="code">{SNIPPETS[snippet](fullUrl)}</pre>
      </div>
    </div>
  )
}
