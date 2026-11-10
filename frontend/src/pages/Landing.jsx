import { useState } from 'react'
import { Link } from 'react-router'
import { getJson } from '../api'
import Playground from '../components/Playground'
import RegionSelect from '../components/RegionSelect'
import { daysBetween, formatDate, formatLongDate } from '../format'
import { guessRegion, REGIONS } from '../regions'
import useLoad from '../useLoad'

const regionName = (code) => REGIONS.find(([c]) => c === code)?.[1] ?? code

export default function Landing() {
  const [region, setRegion] = useState(guessRegion)
  return (
    <>
      <section className="hero">
        <h1>Canadian stat holidays, as an API.</h1>
        <p className="lead">
          Statutory holidays for every province and territory, the day off when one lands on a weekend, and
          business-day maths. Free, documented, with a typed Python SDK.
        </p>
        <NextHoliday region={region} onRegion={setRegion} />
        <div className="hero-actions">
          <a href="#try" className="button big">Try it live</a>
          <a href="/docs" className="button big secondary">API reference</a>
        </div>
        <p className="muted small">No key needed to start: 100 requests an hour. A free key raises that to 1,000.</p>
      </section>

      <section className="section" id="try">
        <h2>Try it</h2>
        <p className="muted">Real requests to the API, from your browser. Pick an example or edit the URL.</p>
        <Playground region={region} />
      </section>

      <section className="section">
        <YearTable region={region} onRegion={setRegion} />
      </section>

      <section className="section">
        <ul className="features">
          <li><h3>Every jurisdiction</h3><p>13 provinces and territories plus federally regulated workplaces, 2023 to 2050.</p></li>
          <li><h3>Statutory vs optional</h3><p>Which days are paid holidays by law, and which are only widely observed.</p></li>
          <li><h3>Observed dates</h3><p>Boxing Day on a Saturday is a Monday off. Each region's shift rules are built in.</p></li>
          <li><h3>Business days</h3><p>Count working days in a range, or add 10 business days to a date.</p></li>
          <li><h3>Plays well with HTTP</h3><p>ETags and 304s, rate-limit headers, Link pagination, problem+json errors.</p></li>
          <li><h3>Typed SDK</h3><p>A Python client generated from the OpenAPI spec, so it can't drift from the API.</p></li>
        </ul>
        <p className="center-text">
          <Link to="/guide">Read the guide</Link> or <Link to="/portal">get a free API key</Link>.
        </p>
      </section>
    </>
  )
}

function NextHoliday({ region, onRegion }) {
  const { data, error } = useLoad(() => getJson(`/v1/regions/${region}/holidays/next`), [region])
  const next = data?.data[0]
  return (
    <div className="next-card card">
      <label className="inline">
        Next statutory holiday in <RegionSelect value={region} onChange={onRegion} />
      </label>
      {error && <p className="error">{error.message}</p>}
      {next ? (
        <div className="next-holiday" aria-live="polite">
          <strong>{next.name}</strong>
          <span>{formatLongDate(next.date)}</span>
          <span className="muted">
            {(() => {
              const days = daysBetween(data.after, next.date)
              return days === 1 ? 'tomorrow' : `in ${days} days`
            })()}
            {next.observed_date !== next.date && `, observed ${formatDate(next.observed_date)}`}
          </span>
        </div>
      ) : (
        !error && <div className="next-holiday muted">Loading…</div>
      )}
    </div>
  )
}

function YearTable({ region, onRegion }) {
  const [year, setYear] = useState(new Date().getFullYear())
  const { data, error } = useLoad(() => getJson(`/v1/regions/${region}/holidays?year=${year}`), [region, year])
  return (
    <div className="card stack">
      <div className="row spread">
        <h2 style={{ margin: 0 }}>{year} holidays in {regionName(region)}</h2>
        <div className="row">
          <RegionSelect value={region} onChange={onRegion} />
          <select value={year} onChange={(e) => setYear(Number(e.target.value))} aria-label="Year">
            {Array.from({ length: 6 }, (_, i) => new Date().getFullYear() - 1 + i).map((y) => (
              <option key={y}>{y}</option>
            ))}
          </select>
        </div>
      </div>
      {error && <p className="error">{error.message}</p>}
      {data && (
        <table className="data-table holiday-table">
          <thead>
            <tr><th>Date</th><th>Holiday</th><th>Type</th><th>Day off</th></tr>
          </thead>
          <tbody>
            {data.data.map((h) => (
              <tr key={h.id} className={h.type}>
                <td className="nowrap">{formatDate(h.date)}</td>
                <td>
                  {h.name}
                  {h.note && <span className="block muted small">{h.note}</span>}
                </td>
                <td><span className={`badge ${h.type}`}>{h.type}</span></td>
                <td className="nowrap">{h.observed_date !== h.date ? formatDate(h.observed_date) : 'Same day'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
