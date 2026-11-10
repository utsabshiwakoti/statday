import { useState } from 'react'
import { callApi, portal } from '../api'
import { useAuth } from '../auth'
import { ChartCard, ColumnChart, DataTable } from '../components/Charts'
import { formatDate, formatNumber } from '../format'
import useLoad from '../useLoad'

export default function Portal() {
  const { developer, loading } = useAuth()
  if (loading) return <div className="centered muted">Loading…</div>
  return developer ? <Dashboard /> : <AuthForm />
}

function AuthForm() {
  const { login, signup } = useAuth()
  const [mode, setMode] = useState('signup')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await (mode === 'signup' ? signup : login)(email, password)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="card auth-card stack">
        <div>
          <h1>{mode === 'signup' ? 'Get a free API key' : 'Sign in'}</h1>
          <p className="muted">
            {mode === 'signup'
              ? 'Keys raise your limit to 1,000 requests an hour and show your usage over time.'
              : 'Manage your keys and see your usage.'}
          </p>
        </div>
        <form className="stack" onSubmit={submit}>
          <label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" /></label>
          <label>
            Password
            <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} />
            {mode === 'signup' && <span className="muted small">At least 8 characters.</span>}
          </label>
          {error && <p className="error" role="alert">{error}</p>}
          <button className="button" disabled={busy}>{mode === 'signup' ? 'Create account' : 'Sign in'}</button>
        </form>
        <p className="small center-text">
          {mode === 'signup' ? 'Already have an account? ' : 'New here? '}
          <button className="link-button" onClick={() => { setMode(mode === 'signup' ? 'login' : 'signup'); setError(null) }}>
            {mode === 'signup' ? 'Sign in' : 'Create an account'}
          </button>
        </p>
      </div>
    </div>
  )
}

function Dashboard() {
  const { developer, logout } = useAuth()
  const keys = useLoad(() => portal('/keys'), [])
  const usage = useLoad(() => portal('/usage', { params: { days: 30 } }), [])
  const [newKey, setNewKey] = useState(null) // the full key, shown once

  const afterKeyChange = (created) => {
    if (created) setNewKey(created)
    keys.reload()
  }

  return (
    <div className="portal stack-lg">
      <div className="page-head">
        <div>
          <h1>Developer portal</h1>
          <p className="muted">{developer.email}</p>
        </div>
        <button className="button secondary" onClick={logout}>Sign out</button>
      </div>

      {newKey && <NewKey created={newKey} onDone={() => setNewKey(null)} />}

      <Keys state={keys} onChange={afterKeyChange} limit={developer.limits.max_keys} />

      <UsageSection usage={usage} keys={keys.data || []} limits={developer.limits} />

      <TryKey initialKey={newKey?.key} onSent={usage.reload} />
    </div>
  )
}

function NewKey({ created, onDone }) {
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    await navigator.clipboard.writeText(created.key)
    setCopied(true)
  }
  return (
    <section className="card new-key stack" aria-live="polite">
      <h2>Your new key: {created.name}</h2>
      <p>Copy it now. For your security it's stored only as a hash, so it can't be shown again.</p>
      <div className="row">
        <code className="grow key-value">{created.key}</code>
        <button className="button" onClick={copy}>{copied ? 'Copied' : 'Copy'}</button>
      </div>
      <pre className="code">{`curl -H "X-API-Key: ${created.key}" ${window.location.origin}/v1/regions/NS/holidays/next`}</pre>
      <div><button className="link-button" onClick={onDone}>I've saved it</button></div>
    </section>
  )
}

function Keys({ state, onChange, limit }) {
  const [name, setName] = useState('')
  const [error, setError] = useState(null)
  const active = (state.data || []).filter((k) => !k.revoked_at)

  const act = async (fn) => {
    setError(null)
    try {
      onChange(await fn())
      return true
    } catch (err) {
      setError(err.message)
      return false
    }
  }

  const create = (e) => {
    e.preventDefault()
    act(() => portal('/keys', { method: 'POST', body: { name } })).then((ok) => ok && setName(''))
  }
  const rotate = (key) => {
    if (window.confirm(`Rotate "${key.name}"? The current key stops working immediately.`)) {
      act(() => portal(`/keys/${key.id}/rotate`, { method: 'POST' }))
    }
  }
  const revoke = (key) => {
    if (window.confirm(`Revoke "${key.name}"? Apps using it will get 401 errors.`)) {
      act(() => portal(`/keys/${key.id}`, { method: 'DELETE' }).then(() => null))
    }
  }

  return (
    <section className="card stack">
      <div className="row spread">
        <h2 style={{ margin: 0 }}>API keys</h2>
        <span className="muted small">{active.length} of {limit} active</span>
      </div>
      {state.error && <p className="error">{state.error.message}</p>}
      {state.data && state.data.length === 0 && <p className="empty">No keys yet. Create one below.</p>}
      {state.data && state.data.length > 0 && (
        <table className="data-table keys-table">
          <thead>
            <tr><th>Name</th><th>Key</th><th>Created</th><th>Last used</th><th /></tr>
          </thead>
          <tbody>
            {state.data.map((k) => (
              <tr key={k.id} className={k.revoked_at ? 'revoked' : ''}>
                <td>{k.name}</td>
                <td><code>{k.prefix}_…</code></td>
                <td className="nowrap">{formatDate(k.created_at.slice(0, 10))}</td>
                <td className="nowrap">{k.last_used_at ? formatDate(k.last_used_at.slice(0, 10)) : 'Never'}</td>
                <td className="actions">
                  {k.revoked_at ? (
                    <span className="badge revoked">Revoked</span>
                  ) : (
                    <>
                      <button className="link-button" onClick={() => rotate(k)}>Rotate</button>
                      <button className="link-button danger-text" onClick={() => revoke(k)}>Revoke</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <form className="row" onSubmit={create}>
        <input className="grow" placeholder="Key name, e.g. Payroll app" required maxLength={60}
          value={name} onChange={(e) => setName(e.target.value)} aria-label="New key name" />
        <button className="button" disabled={active.length >= limit}>Create key</button>
      </form>
      {error && <p className="error" role="alert">{error}</p>}
    </section>
  )
}

function UsageSection({ usage, keys, limits }) {
  if (usage.error) return <p className="error">{usage.error.message}</p>
  if (!usage.data) return <div className="card muted">Loading usage…</div>
  const { days, total, by_key: byKey } = usage.data
  const today = days[days.length - 1].count
  const names = Object.fromEntries(keys.map((k) => [k.id, `${k.name} (${k.prefix})`]))
  const busiest = Object.entries(byKey).sort((a, b) => b[1] - a[1])[0]

  return (
    <>
      <div className="tiles">
        <div className="card tile"><span className="muted small">Requests, last 30 days</span><span className="tile-value">{formatNumber(total)}</span></div>
        <div className="card tile"><span className="muted small">Today (UTC)</span><span className="tile-value">{formatNumber(today)}</span></div>
        <div className="card tile">
          <span className="muted small">Limit per key</span>
          <span className="tile-value">{formatNumber(limits.requests_per_window)}</span>
          <span className="muted small">requests per {limits.window_seconds / 60} minutes</span>
        </div>
        <div className="card tile">
          <span className="muted small">Busiest key</span>
          <span className="tile-value small-value">{busiest ? names[busiest[0]] || 'Deleted key' : '—'}</span>
        </div>
      </div>
      <ChartCard
        title="Requests per day"
        subtitle="All your keys, last 30 days (UTC)"
        table={<DataTable columns={['Day', 'Requests']} rows={[...days].reverse().map((d) => [formatDate(d.day), formatNumber(d.count)])} />}
      >
        <ColumnChart
          ariaLabel={`Requests per day for the last 30 days, ${total} in total`}
          formatAxis={formatNumber}
          data={days.map((d) => ({
            label: formatDate(d.day, { month: 'short', day: 'numeric' }),
            value: d.count,
            tooltip: <><strong>{formatNumber(d.count)} requests</strong><span>{formatDate(d.day)}</span></>,
          }))}
        />
      </ChartCard>
    </>
  )
}

function TryKey({ initialKey, onSent }) {
  const [key, setKey] = useState(initialKey || '')
  const [result, setResult] = useState(null)
  const [lastInitial, setLastInitial] = useState(initialKey)
  // A freshly created key fills the box (adjusting state during render, not in an effect).
  if (initialKey !== lastInitial) {
    setLastInitial(initialKey)
    if (initialKey) setKey(initialKey)
  }

  const send = async (e) => {
    e.preventDefault()
    const res = await callApi('/v1/regions/NS/holidays/next', { key })
    setResult(res)
    onSent()
  }
  const header = (name) => result?.headers.find(([h]) => h === name)?.[1]

  return (
    <section className="card stack">
      <h2 style={{ margin: 0 }}>Test a key</h2>
      <p className="muted">Sends a request with the key, so you can see it count towards your usage.</p>
      <form className="row" onSubmit={send}>
        <input className="grow mono" placeholder="sd_..." required value={key} onChange={(e) => setKey(e.target.value)}
          aria-label="API key" spellCheck="false" />
        <button className="button">Send request</button>
      </form>
      {result && (
        <p className={result.ok ? 'success' : 'error'} aria-live="polite">
          {result.status} {result.ok ? `OK: next holiday in Nova Scotia is ${result.body.data[0].name}.` : result.body?.detail}
          {header('ratelimit-remaining') && ` ${header('ratelimit-remaining')} of ${header('ratelimit-limit')} requests left this hour.`}
        </p>
      )}
    </section>
  )
}
