import React, { useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

type ChatResp = { answer: string }
type HealthResp = { ok: boolean }

const presetQuestions = [
  "Vreau o carte despre libertate și control social.",
  "Ce-mi recomanzi dacă iubesc poveștile fantastice?",
  "Vreau o carte despre prietenie și magie.",
  "Ce este 1984?"
]

export default function App() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [k, setK] = useState(3)
  const [health, setHealth] = useState<string>('Unknown')

  const apiBase = useMemo(() => String(API_BASE).replace(/\/$/, ''), [])

  async function doHealth() {
    setHealth('Verific...')
    try {
      const r = await fetch(`${apiBase}/api/health`)
      const j: HealthResp = await r.json()
      setHealth(j.ok ? 'OK' : 'Probleme')
    } catch {
      setHealth('Eroare')
    }
  }

  async function ask(e?: React.FormEvent) {
    e?.preventDefault()
    setLoading(true); setError(''); setAnswer('')
    try {
      const r = await fetch(`${apiBase}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, k, rebuild: false }),
      })
      if (!r.ok) {
        const t = await r.text()
        throw new Error(`${r.status} ${t}`)
      }
      const j: ChatResp = await r.json()
      setAnswer(j.answer)
    } catch (e: any) {
      setError(String(e?.message ?? e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 920, margin: '40px auto', fontFamily: 'Inter, ui-sans-serif, system-ui' }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <h1 style={{ margin: 0 }}>📚 Smart Librarian</h1>
        <button onClick={doHealth} style={{ marginLeft: 'auto' }}>Health: {health}</button>
      </header>

      <section style={{ marginTop: 24, padding: 16, border: '1px solid #e5e7eb', borderRadius: 12 }}>
        <form onSubmit={ask}>
          <label style={{ display: 'block', fontWeight: 600, marginBottom: 8 }}>Întrebarea ta</label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            placeholder="Ex: Vreau o carte despre prietenie și magie"
            style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #d1d5db' }}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 12 }}>
            <label>Top-k:</label>
            <input type="number" min={1} max={8} value={k} onChange={e => setK(Number(e.target.value))}
                   style={{ width: 64 }} />
            <button type="submit" disabled={loading || !question.trim()}>
              {loading ? 'Caut...' : 'Trimite'}
            </button>
          </div>
        </form>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
          {presetQuestions.map((q, i) => (
            <button key={i} onClick={() => setQuestion(q)} style={{ fontSize: 12 }}>
              {q}
            </button>
          ))}
        </div>
      </section>

      <section style={{ marginTop: 16, padding: 16, border: '1px solid #e5e7eb', borderRadius: 12 }}>
        <h2 style={{ marginTop: 0 }}>Răspuns</h2>
        {error && <pre style={{ color: 'crimson', whiteSpace: 'pre-wrap' }}>{error}</pre>}
        {!error && <article style={{ whiteSpace: 'pre-wrap' }}>{answer || '—'}</article>}
      </section>

      <footer style={{ marginTop: 24, color: '#6b7280', fontSize: 12 }}>
        <div>Backend: <code>FastAPI</code> pe <code>localhost:8000</code>. Frontend: <code>Vite + React</code> pe <code>localhost:5173</code>.</div>
        <div>Setează <code>VITE_API_BASE</code> în <code>.env</code> (frontend) dacă backend-ul nu rulează pe default.</div>
      </footer>
    </div>
  )
}
