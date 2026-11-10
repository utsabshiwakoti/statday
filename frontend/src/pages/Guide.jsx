import { Link } from 'react-router'

// Every problem `type` the API returns points at one of these ids (/guide#rate-limited...).
const ERRORS = [
  ['invalid-parameters', 422, 'A path or query parameter is missing or has the wrong form, like region=XX or a malformed date. `errors` lists each one with its location (e.g. "query.year").'],
  ['out-of-range', 422, 'The year is outside 2023 to 2050. Older years used different rules (Sept 30 wasn\'t a holiday yet), and later ones would be guesses.'],
  ['invalid-range', 422, '`end` is before `start`, or the range is longer than 5 years.'],
  ['unknown-holiday', 404, 'No holiday has that id. The ids are in every holiday response, e.g. `canada-day` or `family-day`.'],
  ['invalid-key', 401, 'The X-API-Key header holds a key that doesn\'t exist or was revoked. Remove the header to fall back to the anonymous limit, or create a new key.'],
  ['rate-limited', 429, 'You\'ve used this window\'s allowance. Wait the number of seconds in `Retry-After` (the same as `RateLimit-Reset`).'],
]

const Code = ({ children }) => <pre className="code">{children}</pre>

export default function Guide() {
  return (
    <div className="guide">
      <aside className="toc">
        <nav aria-label="Guide sections">
          {[['quickstart', 'Quick start'], ['authentication', 'Authentication'], ['rate-limits', 'Rate limits'],
            ['caching', 'Caching'], ['pagination', 'Pagination'], ['errors', 'Errors'], ['versioning', 'Versioning'],
            ['sdk', 'Python SDK'], ['data', 'About the data']].map(([id, label]) => (
            <a key={id} href={`#${id}`}>{label}</a>
          ))}
        </nav>
      </aside>

      <article className="prose">
        <h1>Guide</h1>
        <p className="lead-left">
          Everything beyond the endpoint list. For each endpoint's parameters and response fields, see the{' '}
          <a href="/docs">interactive API reference</a> (or <a href="/redoc">ReDoc</a>).
        </p>

        <section id="quickstart">
          <h2>Quick start</h2>
          <p>No signup needed. Ask for this year's holidays in Nova Scotia:</p>
          <Code>{`curl ${window.location.origin}/v1/regions/NS/holidays`}</Code>
          <p>
            Region codes are the two-letter postal abbreviations, plus <code>CA</code> for federally regulated
            workplaces (banks, airlines, telecoms) under the Canada Labour Code. Dates are ISO 8601 (<code>2026-12-25</code>).
          </p>
        </section>

        <section id="authentication">
          <h2>Authentication</h2>
          <p>
            Keys are optional. Without one, each IP address gets 100 requests an hour. With a free key from
            the <Link to="/portal">developer portal</Link>, you get 1,000 an hour and a usage history.
          </p>
          <Code>{`curl -H "X-API-Key: sd_3f9a1c2e_..." ${window.location.origin}/v1/regions/ON/holidays/next`}</Code>
          <p>
            Keys are shown once, when created. The server keeps only a SHA-256 hash. If a key leaks, <em>rotate</em> it
            in the portal: the old one stops working at once and a new one with the same name takes its place.
          </p>
        </section>

        <section id="rate-limits">
          <h2>Rate limits</h2>
          <p>Every response says where you stand:</p>
          <Code>{`RateLimit-Limit: 1000
RateLimit-Remaining: 997
RateLimit-Reset: 1834          # seconds until the window resets
RateLimit-Policy: 1000;w=3600  # 1000 requests per 3600-second window`}</Code>
          <p>
            Windows start on the hour. Over the limit you get <code>429</code> with a <code>Retry-After</code> header.
            Well-behaved clients wait that long rather than retrying in a loop.
          </p>
        </section>

        <section id="caching">
          <h2>Caching</h2>
          <p>
            Holiday data rarely changes, so every response has an <code>ETag</code> (a fingerprint of the body) and
            a <code>Cache-Control</code> lifetime. Send the ETag back and, if nothing changed, you get an empty{' '}
            <code>304 Not Modified</code> instead of the whole body:
          </p>
          <Code>{`curl -i ${window.location.origin}/v1/regions/NS/holidays?year=2026
# ETag: "9c1f0e..."

curl -i -H 'If-None-Match: "9c1f0e..."' ${window.location.origin}/v1/regions/NS/holidays?year=2026
# HTTP/1.1 304 Not Modified`}</Code>
          <p>Browsers and most HTTP libraries with a cache do this for you.</p>
        </section>

        <section id="pagination">
          <h2>Pagination</h2>
          <p>
            <code>GET /v1/holidays</code> searches across the country and can span up to 5 years, so it's paginated
            with <code>page</code> and <code>per_page</code> (up to 100). The body has a <code>pagination</code> object, and
            the headers carry the same information for generic clients:
          </p>
          <Code>{`X-Total-Count: 32
Link: </v1/holidays?per_page=10&page=1>; rel="first", </v1/holidays?per_page=10&page=3>; rel="next", ...`}</Code>
          <p>Follow <code>rel="next"</code> until it's missing.</p>
        </section>

        <section id="errors">
          <h2>Errors</h2>
          <p>
            Errors use one format everywhere: <code>application/problem+json</code> from{' '}
            <a href="https://www.rfc-editor.org/rfc/rfc9457">RFC 9457</a>. Switch on <code>type</code>; show{' '}
            <code>detail</code> to people.
          </p>
          <Code>{`{
  "type": "/guide#out-of-range",
  "title": "Out of range",
  "status": 422,
  "detail": "Years 2023 to 2050 are supported; got 1999.",
  "instance": "/v1/regions/NS/holidays"
}`}</Code>
          <dl className="error-list">
            {ERRORS.map(([slug, status, text]) => (
              <div key={slug} id={slug}>
                <dt><code>{slug}</code> <span className="badge">{status}</span></dt>
                <dd>{text.split('`').map((part, i) => (i % 2 ? <code key={i}>{part}</code> : part))}</dd>
              </div>
            ))}
          </dl>
        </section>

        <section id="versioning">
          <h2>Versioning</h2>
          <p>
            Paths start with <code>/v1</code>. Within v1, changes are additive only: new endpoints, new optional
            parameters, new response fields. Clients should ignore fields they don't know. Anything that would
            break a client (renaming or removing a field, changing a meaning) would ship as <code>/v2</code>, with v1
            kept running alongside it.
          </p>
          <p>Corrections to holiday data (a province adds a holiday) are data changes, not version changes.</p>
        </section>

        <section id="sdk">
          <h2>Python SDK</h2>
          <p>
            A typed client generated from the <a href="/openapi.json">OpenAPI spec</a>, in the{' '}
            <a href="https://github.com/utsabshiwakoti/statday/tree/main/sdk">sdk folder</a> of the repository.
          </p>
          <Code>{`from datetime import date

from statday_client import Client
from statday_client.api.business_days import add_business_days
from statday_client.models import RegionCode

with Client(base_url="${window.location.origin}") as client:
    due = add_business_days.sync(client=client, region=RegionCode.ON, start=date(2026, 12, 23), days=3)
    print(due.result)  # 2026-12-30: skips Christmas and Boxing Day (observed Monday the 28th)`}</Code>
        </section>

        <section id="data">
          <h2>About the data</h2>
          <ul>
            <li><strong>Statutory</strong> means a paid general holiday under the region's employment standards law. <strong>Optional</strong> means widely observed (government offices, banks, many employers) but not guaranteed.</li>
            <li><strong>Observed dates.</strong> When a holiday falls on a weekend, most regions give the next working day off. Remembrance Day never moves. In Quebec, only holidays on a Sunday move. When Christmas and Boxing Day both land on a weekend, they take Monday and Tuesday.</li>
            <li><strong>Business days</strong> skip weekends and statutory days off (the observed day, for moved holidays).</li>
            <li>Rules were checked in November 2026 against federal, provincial and territorial sources. Years after that are projections of current law. This is a reference, not legal advice.</li>
          </ul>
        </section>
      </article>
    </div>
  )
}
