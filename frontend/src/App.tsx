import { useEffect, useState, type FormEvent } from 'react';
import { createPlan, extractStudentRecord, getIntegrationStatus } from './api/client';
import type { ExtractionResponse, IntegrationStatus, PlanResponse, StudentRecord, StudentUnit, UnitStatus } from './types';

const emptyUnit = (): StudentUnit => ({ code: '', status: 'completed', mark: null, credit_points: 6 });

function stateLabel(state?: string) {
  if (state === 'online') return 'Live';
  if (state === 'demo') return 'Demo';
  return 'Offline';
}

export default function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [extraction, setExtraction] = useState<ExtractionResponse | null>(null);
  const [record, setRecord] = useState<StudentRecord | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [session, setSession] = useState<'Semester 1' | 'Semester 2'>('Semester 1');
  const [load, setLoad] = useState(24);
  const [pace, setPace] = useState<'balanced' | 'accelerated'>('balanced');
  const [interests, setInterests] = useState('machine learning, scalable data');
  const [prompt, setPrompt] = useState('Plan my next semester and explain why each unit is eligible.');
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [status, setStatus] = useState<IntegrationStatus | null>(null);
  const [busy, setBusy] = useState<'extract' | 'plan' | ''>('');
  const [error, setError] = useState('');

  useEffect(() => { getIntegrationStatus().then(setStatus).catch(() => undefined); }, []);

  async function extract(event: FormEvent) {
    event.preventDefault();
    setError(''); setPlan(null);
    if (!files.length || files.length > 2) return setError('Choose a transcript and optionally one progression report.');
    setBusy('extract');
    try {
      const result = await extractStudentRecord(files);
      setExtraction(result); setRecord(result.record); setConfirmed(false);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Could not read the PDFs.'); }
    finally { setBusy(''); }
  }

  function updateUnit(index: number, patch: Partial<StudentUnit>) {
    if (!record) return;
    const units = record.units.map((unit, current) => current === index ? { ...unit, ...patch } : unit);
    setRecord({ ...record, units }); setConfirmed(false); setPlan(null);
  }

  function removeUnit(index: number) {
    if (!record) return;
    setRecord({ ...record, units: record.units.filter((_, current) => current !== index) });
    setConfirmed(false); setPlan(null);
  }

  async function submitPlan(event: FormEvent) {
    event.preventDefault(); setError(''); setPlan(null);
    if (!record || !confirmed) return setError('Confirm the extracted record before planning.');
    if (record.units.some(unit => !/^[A-Z]{4}\d{4}$/.test(unit.code))) return setError('Correct every unit code before planning.');
    setBusy('plan');
    try {
      setPlan(await createPlan({
        prompt, confirmed, record, target_session: session, target_credit_points: load, pace,
        interests: interests.split(',').map(value => value.trim()).filter(Boolean)
      }));
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Could not create the plan.'); }
    finally { setBusy(''); }
  }

  return <main className="shell">
    <header className="hero">
      <div>
        <p className="eyebrow">UniPilot · USYD 2026</p>
        <h1>A course plan that can explain every choice.</h1>
        <p className="lead">Upload your academic record, verify what we found, then build a rule-checked Computational Data Science plan grounded in the official handbook.</p>
      </div>
      <div className="status-card">
        <p className="mini-label">Integration status</p>
        <div className="status-row"><span>Zetaris</span><b data-state={status?.zetaris.state}>{stateLabel(status?.zetaris.state)}</b></div>
        <div className="status-row"><span>Scout Intent</span><b data-state={status?.scout.state}>{stateLabel(status?.scout.state)}</b></div>
        <div className="status-row"><span>Nightshift</span><b data-state={status?.meterless.state}>{stateLabel(status?.meterless.state)}</b></div>
        <small>{status?.mode === 'live' ? 'Live sponsor integrations' : 'Demo adapters active'}</small>
      </div>
    </header>

    <section className="step-card">
      <div className="step-number">1</div>
      <div className="step-content">
        <p className="mini-label">Academic record</p>
        <h2>Upload, then verify</h2>
        <p>Use a redacted transcript and optional progression report. Files are processed in memory and are not stored.</p>
        <form onSubmit={extract} className="upload-row">
          <input type="file" accept="application/pdf,.pdf" multiple onChange={event => setFiles(Array.from(event.target.files ?? []))} />
          <button disabled={busy === 'extract'}>{busy === 'extract' ? 'Reading PDFs…' : 'Extract units'}</button>
        </form>
        {extraction && <div className="notice-stack">
          {extraction.documents.map(document => <p className="notice" key={document.filename}>{document.filename}: {document.units_found} unit(s) found across {document.pages} page(s).</p>)}
          {extraction.warnings.map(warning => <p className="warning" key={warning}>{warning}</p>)}
        </div>}
      </div>
    </section>

    {record && <section className="step-card">
      <div className="step-number">2</div>
      <div className="step-content">
        <p className="mini-label">Human checkpoint</p>
        <h2>Confirm the parsed record</h2>
        <div className="record-table">
          <div className="record-head"><span>Unit</span><span>Status</span><span>Mark</span><span></span></div>
          {record.units.map((unit, index) => <div className="record-row" key={`${index}-${unit.code}`}>
            <input aria-label="Unit code" value={unit.code} maxLength={8} onChange={event => updateUnit(index, { code: event.target.value.toUpperCase() })} />
            <select aria-label="Unit status" value={unit.status} onChange={event => updateUnit(index, { status: event.target.value as UnitStatus })}>
              <option value="completed">Completed</option><option value="current">Current</option><option value="credited">Credit transfer</option><option value="failed">Failed</option><option value="unknown">Needs review</option>
            </select>
            <input aria-label="Mark" type="number" min="0" max="100" value={unit.mark ?? ''} onChange={event => updateUnit(index, { mark: event.target.value ? Number(event.target.value) : null })} />
            <button className="icon-button" type="button" onClick={() => removeUnit(index)}>Remove</button>
          </div>)}
        </div>
        <button className="secondary" type="button" onClick={() => { setRecord({ ...record, units: [...record.units, emptyUnit()] }); setConfirmed(false); }}>+ Add unit</button>
        <label className="confirm"><input type="checkbox" checked={confirmed} onChange={event => setConfirmed(event.target.checked)} /> I checked every unit code, status and mark above.</label>
      </div>
    </section>}

    {record && <section className="step-card">
      <div className="step-number">3</div>
      <div className="step-content">
        <p className="mini-label">Scout-routed request</p>
        <h2>Plan the next term</h2>
        <form onSubmit={submitPlan} className="planner-form">
          <label>What do you need?<textarea value={prompt} onChange={event => setPrompt(event.target.value)} /></label>
          <div className="form-grid">
            <label>Target session<select value={session} onChange={event => setSession(event.target.value as typeof session)}><option>Semester 1</option><option>Semester 2</option></select></label>
            <label>Study load<select value={load} onChange={event => setLoad(Number(event.target.value))}><option value="12">12 credit points</option><option value="18">18 credit points</option><option value="24">24 credit points</option></select></label>
            <label>Pace<select value={pace} onChange={event => setPace(event.target.value as typeof pace)}><option value="balanced">Balanced</option><option value="accelerated">Accelerated</option></select></label>
          </div>
          <label>Interests<input value={interests} onChange={event => setInterests(event.target.value)} /></label>
          <button disabled={!confirmed || busy === 'plan'}>{busy === 'plan' ? 'Checking rules…' : 'Build my verified plan'}</button>
        </form>
      </div>
    </section>}

    {error && <p className="error" role="alert">{error}</p>}

    {plan?.status === 'clarification' && <section className="result-card"><h2>{plan.clarification?.question}</h2><div className="pill-row">{plan.clarification?.options.map(option => <span key={option}>{option}</span>)}</div></section>}
    {plan?.status === 'complete' && <section className="result-card">
      <div className="result-heading"><div><p className="eyebrow">Verified next term</p><h2>{session} · {plan.next_term.reduce((sum, unit) => sum + unit.credit_points, 0)} credit points</h2></div><span className="verified">Rule-checked</span></div>
      <p className="narrative">{plan.narrative}</p>
      <div className="unit-grid">{plan.next_term.map(unit => <article className="unit-card" key={unit.code}><div><span>{unit.requirement_group}</span><h3>{unit.code}</h3><p>{unit.title}</p></div><p>{unit.reason}</p><a href={unit.source_url} target="_blank" rel="noreferrer">Official handbook ↗</a></article>)}</div>
      {!plan.next_term.length && <p className="warning">No eligible unit fit the selected session and load. Review the excluded-unit reasons.</p>}
      <div className="result-columns">
        <div><h3>Indicative outlook</h3>{plan.outlook.map(term => <div key={term.session}><b>{term.session}</b><p>{term.units.join(' · ') || 'No eligible catalogue units yet'}</p><small>{term.note}</small></div>)}</div>
        <div><h3>Why options were excluded</h3>{plan.excluded.slice(0, 5).map(unit => <p key={unit.code}><b>{unit.code}</b> — {unit.reason}</p>)}</div>
      </div>
      <details><summary>Decision trace</summary><ol>{plan.trace.map(step => <li key={step}>{step}</li>)}</ol><small>Scout contract: {plan.contract_id}</small></details>
      <div className="evidence-row">{plan.evidence.map(item => <a href={item.url} key={item.url} target="_blank" rel="noreferrer">{item.label}</a>)}</div>
    </section>}
  </main>;
}
