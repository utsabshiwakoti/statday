// API dates are plain "YYYY-MM-DD" strings. Format them as UTC so the browser's own time zone
// can't shift them to the day before.
const parse = (iso) => new Date(`${iso}T00:00:00Z`)

export const formatDate = (iso, options = { weekday: 'short', month: 'short', day: 'numeric' }) =>
  parse(iso).toLocaleDateString('en-US', { timeZone: 'UTC', ...options })

export const formatLongDate = (iso) =>
  formatDate(iso, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })

/** Whole days from one ISO date to another. */
export const daysBetween = (from, to) => Math.round((parse(to) - parse(from)) / 86_400_000)

/** Today's date as YYYY-MM-DD in the browser's time zone (en-CA formats dates that way). */
export const todayIso = () => new Date().toLocaleDateString('en-CA')

export const formatNumber = (n) => n.toLocaleString('en-US')
