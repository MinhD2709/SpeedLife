import { useState, type FormEvent } from 'react';
import { createCheatSheet } from './api/client';
import PdfUpload from './components/PdfUpload';
import CheatSheetView from './components/CheatSheetView';
import type { CheatSheet } from './types';

export default function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [title, setTitle] = useState('My lecture cheat sheet');
  const [sheet, setSheet] = useState<CheatSheet | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(''); setSheet(null);
    if (!files.length || files.length > 5) { setError('Choose between 1 and 5 PDFs.'); return; }
    if (files.some(file => file.size > 15 * 1024 * 1024) || files.reduce((n, file) => n + file.size, 0) > 30 * 1024 * 1024) {
      setError('Use files below 15 MB each and 30 MB combined.'); return;
    }
    setBusy(true);
    try { setSheet(await createCheatSheet(files, title)); }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to create cheat sheet.'); }
    finally { setBusy(false); }
  }
  return <main>
    <header><p>Open Agent Hackathon · SpeedLife</p><h1>Lectures, condensed.</h1>
      <p>Upload lecture PDFs and build a cheat sheet with page references.</p>
      <p className="badge">Scaffold demo: source excerpts only. Live AI and sponsor connections need implementation.</p>
    </header>
    <form onSubmit={submit}>
      <label>Sheet title<input maxLength={120} value={title} disabled={busy} onChange={event => setTitle(event.target.value)} /></label>
      <PdfUpload disabled={busy} onChange={setFiles} />
      <button disabled={busy || !files.length}>{busy ? 'Processing lectures…' : 'Create cheat sheet'}</button>
    </form>
    <p role="status" aria-live="polite">{busy ? 'Extracting and checking page references…' : ''}</p>
    {error && <p role="alert">{error}</p>}
    {sheet && <CheatSheetView sheet={sheet} />}
  </main>;
}
