import type { CheatSheet } from '../types';
export default function CheatSheetView({ sheet }: { sheet: CheatSheet }) {
  return <section aria-label="Cheat sheet">
    <h2>{sheet.title}</h2><p className="badge">Mode: {sheet.mode}</p>
    {sheet.warnings.map((warning, i) => <p key={i} role="note">{warning}</p>)}
    <ol>{sheet.points.map((point, i) => <li key={i}>
      <p>{point.text}</p><small>{point.citation.filename} · page {point.citation.page}</small>
      <details><summary>Source evidence</summary><blockquote>{point.citation.text}</blockquote></details>
    </li>)}</ol>
    <details><summary>Processing steps</summary><ul>{sheet.trace.map((step, i) => <li key={i}>{step}</li>)}</ul></details>
    <button onClick={() => window.print()}>Print / save as PDF</button>
  </section>;
}
