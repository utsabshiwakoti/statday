import { useEffect } from 'react'
import { Link, NavLink, Route, Routes, useLocation } from 'react-router'
import Guide from './pages/Guide'
import Landing from './pages/Landing'
import Portal from './pages/Portal'

function ScrollToHash() {
  // Problem `type` links (/guide#rate-limited) should land on the right section.
  const { pathname, hash } = useLocation()
  useEffect(() => {
    if (hash) document.getElementById(hash.slice(1))?.scrollIntoView()
    else window.scrollTo(0, 0)
  }, [pathname, hash])
  return null
}

export default function App() {
  return (
    <>
      <ScrollToHash />
      <header className="topbar">
        <Link to="/" className="brand">
          <img src="/favicon.svg" alt="" width="26" height="26" /> StatDay
        </Link>
        <nav>
          <NavLink to="/guide">Guide</NavLink>
          {/* FastAPI serves these, so they're plain links rather than client-side routes. */}
          <a href="/docs">API reference</a>
          <NavLink to="/portal" className="button small">Get a key</NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/guide" element={<Guide />} />
          <Route path="/portal" element={<Portal />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <footer className="footer">
        <span>StatDay · Canadian holidays API</span>
        <span>
          <a href="/docs">Swagger UI</a> · <a href="/redoc">ReDoc</a> · <a href="/openapi.json">OpenAPI</a> ·{' '}
          <a href="https://github.com/utsabshiwakoti/statday">GitHub</a>
        </span>
      </footer>
    </>
  )
}

function NotFound() {
  return (
    <div className="centered">
      <div className="stack" style={{ textAlign: 'center' }}>
        <h1>Page not found</h1>
        <Link to="/">Back to the home page</Link>
      </div>
    </div>
  )
}
