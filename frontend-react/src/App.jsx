import { useState, useEffect } from 'react'
import './App.css'

const API_URL = "https://lyrics-generator-backend-2.onrender.com"

function parseLyrics(raw) {
  if (!raw) return []
  const lines = raw.split('\n')
  const sections = []
  let current = null

  for (let line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    const labelMatch = trimmed.match(/^\[(.+)\]$/)
    if (labelMatch) {
      current = { label: labelMatch[1], lines: [] }
      sections.push(current)
    } else {
      if (!current) {
        current = { label: '', lines: [] }
        sections.push(current)
      }
      current.lines.push(trimmed)
    }
  }
  return sections
}

function App() {
  const [singer, setSinger] = useState('')
  const [mood, setMood] = useState('')
  const [topic, setTopic] = useState('')
  const [view, setView] = useState('landing') // 'landing' | 'loading' | 'result'
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [showScrollHint, setShowScrollHint] = useState(true)

  useEffect(() => {
    document.body.style.overflow = view === 'loading' ? 'hidden' : 'auto'
  }, [view])

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollHint(window.scrollY < 80)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!singer || !mood || !topic) {
      setError('Please complete every field before searching the archive.')
      return
    }
    setError('')
    setResult(null)
    setView('loading')

    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ singer, mood, topic }),
      })
      const data = await response.json()
      setResult(data)
      setView('result')
      window.scrollTo(0, 0)
    } catch (err) {
      setError('Could not reach the backend. Is it running?')
      setView('landing')
    }
  }

  const handleGenerateNew = () => {
    setResult(null)
    setError('')
    setSinger('')
    setMood('')
    setTopic('')
    setView('landing')
    window.scrollTo(0, 0)
  }

  const sections = result?.lyrics ? parseLyrics(result.lyrics) : []

  if (view === 'loading') {
    return (
      <div className="loading-screen">
        <div className="loading-mark" />
        <p className="loading-text">Searching the archive and composing your verse…</p>
      </div>
    )
  }

  if (view === 'result' && result) {
    return (
      <div className="result-page">
        <div className="result-inner">
          {result.status === 'found_in_database' && (
            <>
              <header className="hero result-hero">
                <div className="tab" />
                <h1>{result.corrected_singer}</h1>
                <p className="subtitle">{mood} · {topic}</p>
              </header>

              {result.corrected_singer.toLowerCase() !== singer.toLowerCase() && (
                <p className="correction">Filed under <strong>{result.corrected_singer}</strong></p>
              )}

              <div className="catalog">
                <p className="catalog-label">Reference tracks pulled from the archive</p>
                <div className="catalog-cards">
                  {result.songs_used.map((title, i) => (
                    <div className="catalog-card" key={i}>
                      <span className="catalog-index">{String(i + 1).padStart(2, '0')}</span>
                      <span className="catalog-title">{title}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="sheet">
                {sections.map((s, i) => (
                  <div className="section" key={i}>
                    {s.label && <p className="section-label">{s.label}</p>}
                    {s.lines.map((line, j) => (
                      <p className="lyric-line" key={j}>{line}</p>
                    ))}
                  </div>
                ))}
              </div>
            </>
          )}

          {result.status === 'known_artist_no_database' && (
            <>
              <header className="hero result-hero">
                <div className="tab" />
                <h1>{result.corrected_singer}</h1>
                <p className="subtitle">{mood} · {topic}</p>
              </header>

              <p className="notice">
                <strong>{result.corrected_singer}</strong> has no reference tracks in the archive —
                this verse is composed from general style knowledge instead.
              </p>

              <div className="sheet">
                {sections.map((s, i) => (
                  <div className="section" key={i}>
                    {s.label && <p className="section-label">{s.label}</p>}
                    {s.lines.map((line, j) => (
                      <p className="lyric-line" key={j}>{line}</p>
                    ))}
                  </div>
                ))}
              </div>
            </>
          )}

          {result.status === 'unknown_artist' && (
            <p className="error">{result.message}</p>
          )}

          {result.status === 'error' && (
            <p className="error">{result.message}</p>
          )}

          <button type="button" className="cta secondary" onClick={handleGenerateNew}>
            Generate a new one
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="landing">
      <section className="title-section">
        <div className="tab" />
        <h1>The Songwriter's Archive</h1>
        <p className="subtitle">Generate Lyrics Just Like Your Favorite Artists</p>
      </section>

      <div className={`scroll-hint ${showScrollHint ? 'visible' : 'hidden'}`}>scroll to begin ↓</div>

      <section className="form-section">
        <div className="card">
          <form onSubmit={handleSubmit} className="form">
            <div className="form-row">
              <div className="field">
                <label>The Artist</label>
                <input
                  type="text"
                  placeholder="Taylor Swift, Ed Sheeran, Adele…"
                  value={singer}
                  onChange={(e) => setSinger(e.target.value)}
                />
              </div>

              <div className="field">
                <label>The Mood</label>
                <input
                  type="text"
                  placeholder="Love, Happy, Sad, Emotional…"
                  value={mood}
                  onChange={(e) => setMood(e.target.value)}
                />
              </div>
            </div>

            <div className="field">
              <label>The Topic for the Lyrics</label>
              <textarea
                placeholder="A Wonderful Day, Heartbreak, Friendship…"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                rows={3}
              />
            </div>

            <div className="divider" />

            <button type="submit" className="cta">
              Generate Lyrics
            </button>
          </form>

          {error && <p className="error">{error}</p>}
        </div>
      </section>

      <footer className="footer">
        <p>Casellite</p>
        <p className="copyright">© {new Date().getFullYear()} The Songwriter's Archive</p>
      </footer>
    </div>
  )
}

export default App