import React, { useMemo, useState } from 'react'
import { signPayload } from './signing.js'

function LabelInput({ label, value, onChange, placeholder }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} />
    </label>
  )
}

function Section({ title, children }) {
  return (
    <section>
      <h2>{title}</h2>
      {children}
    </section>
  )
}

function canonicalJSONStringify(obj) {
  const sort = (v) => {
    if (Array.isArray(v)) return v.map(sort)
    if (v && typeof v === 'object') {
      return Object.keys(v)
        .sort()
        .reduce((acc, k) => {
          acc[k] = sort(v[k])
          return acc
        }, {})
    }
    return v
  }
  return JSON.stringify(sort(obj))
}

function randomIdemKey() {
  return 'idem-' + Math.random().toString(36).slice(2) + Date.now().toString(36)
}

export default function App() {
  const [mode, setMode] = useState('demo')
  const [apiBase, setApiBase] = useState('http://localhost:8000')
  const [keyId, setKeyId] = useState('urn:coop:demo-a')
  const [privateKeyB64, setPrivateKeyB64] = useState('')

  const [fromOrg, setFromOrg] = useState('urn:coop:demo-a')
  const [toOrg, setToOrg] = useState('urn:coop:demo-b')
  const [total, setTotal] = useState('300')
  const [story, setStory] = useState('Demo trade')

  const [invoices, setInvoices] = useState([])
  const [trust, setTrust] = useState(null)
  const [checkpointResult, setCheckpointResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copyCurl, setCopyCurl] = useState('')

  const demoInvoices = useMemo(
    () => [
      { id: '1001', from_org: 'urn:coop:demo-a', to_org: 'urn:coop:demo-b', total: 300, status: 'proposed' },
      { id: '1000', from_org: 'urn:coop:demo-b', to_org: 'urn:coop:demo-a', total: 120, status: 'accepted' },
    ],
    []
  )

  async function listInvoices() {
    setError('')
    setLoading(true)
    try {
      if (mode === 'demo') {
        setInvoices(demoInvoices)
      } else {
        const res = await fetch(`${apiBase}/invoices`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setInvoices(data.items || [])
      }
    } catch (e) {
      setError(String(e.message || e))
    } finally {
      setLoading(false)
    }
  }

  async function createInvoice() {
    setError('')
    setLoading(true)
    try {
      if (mode === 'demo') {
        const next = { id: String(1000 + Math.floor(Math.random() * 1000)), from_org: fromOrg, to_org: toOrg, total: Number(total), status: 'proposed', story }
        setInvoices([next, ...invoices])
        return
      }
      const payload = {
        from_org: fromOrg,
        to_org: toOrg,
        lines: [{ description: story || 'Demo line', amount: Number(total) }],
        total: Number(total),
        terms: {},
        story,
        signatures: [],
      }
      const canon = canonicalJSONStringify(payload)
      const { signatureB64 } = await signPayload(canon, privateKeyB64)
      const res = await fetch(`${apiBase}/invoices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Idempotency-Key': randomIdemKey(),
          'X-Key-Id': keyId,
          'X-Signature': signatureB64,
        },
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      await listInvoices()
      setCopyCurl(`http POST ${apiBase}/invoices Idempotency-Key:${randomIdemKey()} X-Key-Id:${keyId} X-Signature:${signatureB64} < <(cat <<'JSON'\n${JSON.stringify(payload, null, 2)}\nJSON\n)`) 
    } catch (e) {
      setError(String(e.message || e))
    } finally {
      setLoading(false)
    }
  }

  async function acceptInvoice(id) {
    setError('')
    setLoading(true)
    try {
      const body = {}
      const canon = canonicalJSONStringify(body)
      const { signatureB64 } = await signPayload(canon, privateKeyB64)
      const res = await fetch(`${apiBase}/invoices/${id}/accept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Key-Id': keyId, 'X-Signature': signatureB64 },
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      await listInvoices()
      setCopyCurl(`http POST ${apiBase}/invoices/${id}/accept X-Key-Id:${keyId} X-Signature:${signatureB64} < <(echo '{}')`)
    } catch (e) { setError(String(e.message || e)) } finally { setLoading(false) }
  }

  async function postAttestation(invoiceId) {
    setError('')
    setLoading(true)
    try {
      const payload = { subject_type: 'invoice', subject_id: String(invoiceId), claims: [{ claim: 'quantity_verified', value: { received: 200, expected: 200 }, confidence: 1.0 }], weight: 1.0 }
      const canon = canonicalJSONStringify(payload)
      const { signatureB64 } = await signPayload(canon, privateKeyB64)
      const res = await fetch(`${apiBase}/attestations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Key-Id': keyId, 'X-Signature': signatureB64 },
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setCopyCurl(`http POST ${apiBase}/attestations X-Key-Id:${keyId} X-Signature:${signatureB64} < <(cat <<'JSON'\n${JSON.stringify(payload, null, 2)}\nJSON\n)`) 
    } catch (e) { setError(String(e.message || e)) } finally { setLoading(false) }
  }

  async function queryTrust() {
    setError('')
    setLoading(true)
    try {
      if (mode === 'demo') {
        setTrust({ score: 0.76, confidence: 'medium', factors: { direct: 0.7, attestations: 0.2, disputes: 0, network: 0.1 } })
      } else {
        const u = new URL(`${apiBase}/trust/score`)
        u.searchParams.set('from_org', fromOrg)
        u.searchParams.set('to_org', toOrg)
        u.searchParams.set('include_factors', 'true')
        const res = await fetch(u)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        setTrust(await res.json())
      }
    } catch (e) {
      setError(String(e.message || e))
    } finally {
      setLoading(false)
    }
  }

  async function generateCheckpoint() {
    setError('')
    setLoading(true)
    try {
      const today = new Date().toISOString().slice(0, 10)
      if (mode === 'demo') {
        setCheckpointResult({ date: today, operations_count: 2, merkle_root: 'demo-root' })
      } else {
        const u = new URL(`${apiBase}/checkpoints/generate`)
        u.searchParams.set('date', today)
        const res = await fetch(u, { method: 'POST' })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        setCheckpointResult(await res.json())
      }
    } catch (e) {
      setError(String(e.message || e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header>
        <div>
          <h1>ICN Demo UI</h1>
          <div className="mode">
            <label><input type="radio" name="mode" checked={mode==='demo'} onChange={() => setMode('demo')} /> Demo</label>
            <label><input type="radio" name="mode" checked={mode==='live'} onChange={() => setMode('live')} /> Live API</label>
          </div>
        </div>
        <div className="live-config" style={{ display: mode==='live' ? 'grid' : 'none' }}>
          <LabelInput label="API Base" value={apiBase} onChange={setApiBase} placeholder="http://localhost:8000" />
          <LabelInput label="X-Key-Id (Org URN)" value={keyId} onChange={setKeyId} placeholder="urn:coop:demo-a" />
          <LabelInput label="Private Key (base64)" value={privateKeyB64} onChange={setPrivateKeyB64} placeholder="Ed25519 secret (32 or 64 bytes)" />
        </div>
      </header>

      {error ? <div style={{ color:'#fda4af' }}>{error}</div> : null}
      {loading ? <div>Loading…</div> : null}

      <main>
        <Section title="Create Invoice">
          <div className="row">
            <LabelInput label="From Org" value={fromOrg} onChange={setFromOrg} placeholder="urn:coop:demo-a" />
            <LabelInput label="To Org" value={toOrg} onChange={setToOrg} placeholder="urn:coop:demo-b" />
            <LabelInput label="Total" value={total} onChange={setTotal} placeholder="300" />
          </div>
          <label className="field" style={{ marginTop: 8 }}>
            <span>Story</span>
            <textarea value={story} onChange={e=>setStory(e.target.value)} rows={3} />
          </label>
          <button onClick={createInvoice}>Create Invoice</button>
        </Section>

        <Section title="Invoices">
          <button onClick={listInvoices}>Refresh</button>
          <table style={{ marginTop: 8 }}>
            <thead>
              <tr><th>ID</th><th>From</th><th>To</th><th>Total</th><th>Status</th></tr>
            </thead>
            <tbody>
              {(mode==='demo' ? demoInvoices : invoices).map((i) => (
                <tr key={i.id}>
                  <td>{i.id}</td>
                  <td>{i.from_org || i.from_org_id}</td>
                  <td>{i.to_org || i.to_org_id}</td>
                  <td>{i.total}</td>
                  <td>
                    <span className={`badge badge-${i.status}`}>{i.status}</span>
                    {mode==='live' ? (
                      <>
                        <button style={{ marginLeft: 8 }} onClick={() => acceptInvoice(i.id)}>Accept</button>
                        <button style={{ marginLeft: 8 }} onClick={() => postAttestation(i.id)}>Attest</button>
                      </>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>

        <Section title="Trust Score">
          <div className="row">
            <LabelInput label="From Org" value={fromOrg} onChange={setFromOrg} />
            <LabelInput label="To Org" value={toOrg} onChange={setToOrg} />
          </div>
          <button onClick={queryTrust}>Query</button>
          {trust ? (
            <div style={{ marginTop: 8 }}>
              <div><b>Score:</b> {trust.score} ({trust.confidence})</div>
              {trust.factors ? (
                <ul className="list">
                  <li>direct: {trust.factors.direct}</li>
                  <li>attestations: {trust.factors.attestations}</li>
                </ul>
              ) : null}
            </div>
          ) : null}
        </Section>

        <Section title="Checkpoint">
          <button onClick={generateCheckpoint}>Generate today</button>
          {checkpointResult ? (
            <div style={{ marginTop: 8 }}>
              <div><b>Date:</b> {checkpointResult.date}</div>
              <div><b>Ops:</b> {checkpointResult.operations_count}</div>
              <div><b>Merkle root:</b> {checkpointResult.merkle_root}</div>
            </div>
          ) : null}
        </Section>

        <Section title="Copy curl for last action">
          <pre style={{ whiteSpace: 'pre-wrap' }}>{copyCurl}</pre>
        </Section>
      </main>

      <footer>
        ICN Demo — Demo mode requires no backend. Live mode calls your node.
      </footer>
    </div>
  )
}