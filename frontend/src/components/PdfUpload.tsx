type Props = { disabled: boolean; onChange: (files: File[]) => void };
export default function PdfUpload({ disabled, onChange }: Props) {
  return <label>Lecture PDFs (up to 5 files, 100 pages each)
    <input type="file" multiple accept="application/pdf,.pdf" disabled={disabled}
      onChange={event => onChange(Array.from(event.target.files ?? []))} />
    <small>15 MB per file; 30 MB total. Text PDFs only; scans need OCR.</small>
  </label>;
}
