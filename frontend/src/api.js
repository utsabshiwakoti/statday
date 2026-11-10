// Two kinds of calls: the portal's private backend (/api, signed in with a token) and the public
// API (/v1, optionally with an API key), where the playground also wants status, headers and timing.

const TOKEN_KEY = 'statday.token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token) =>
  token ? localStorage.setItem(TOKEN_KEY, token) : localStorage.removeItem(TOKEN_KEY)

// Every error from the API is RFC 9457 problem+json: { title, detail, errors? }.
function errorMessage(data, status) {
  if (data?.errors?.length) return data.errors.map((e) => `${e.location}: ${e.message}`).join('; ')
  if (data?.detail) return typeof data.detail === 'string' ? data.detail : data.title
  return `Something went wrong (${status}). Please try again.`
}

export async function portal(path, { method = 'GET', body, form, params } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let payload
  if (form) payload = new URLSearchParams(form)
  else if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }
  const query = params ? `?${new URLSearchParams(params)}` : ''
  const res = await fetch(`/api${path}${query}`, { method, headers, body: payload })
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const error = new Error(errorMessage(data, res.status))
    error.status = res.status
    throw error
  }
  return data
}

const SHOWN_HEADERS = ['content-type', 'etag', 'cache-control', 'ratelimit-limit', 'ratelimit-remaining',
  'ratelimit-reset', 'retry-after', 'x-total-count', 'link']

/** Call the public API and keep everything the playground shows: status, headers, body, time. */
export async function callApi(path, { key } = {}) {
  const started = performance.now()
  // no-store: show the real response each time rather than the browser's cached copy.
  const res = await fetch(path, { headers: key ? { 'X-API-Key': key } : {}, cache: 'no-store' })
  const body = await res.json().catch(() => null)
  const headers = SHOWN_HEADERS.filter((h) => res.headers.has(h)).map((h) => [h, res.headers.get(h)])
  return { ok: res.ok, status: res.status, body, headers, ms: Math.round(performance.now() - started) }
}

/** Plain JSON from the public API, for the page's own widgets. */
export async function getJson(path) {
  const res = await fetch(path)
  const data = await res.json().catch(() => null)
  if (!res.ok) throw new Error(errorMessage(data, res.status))
  return data
}
