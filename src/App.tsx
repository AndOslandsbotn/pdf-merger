import { type ChangeEvent, useCallback, useId, useRef, useState } from "react";
import { mergePdfFiles } from "./mergePdfs";

function downloadBytes(data: Uint8Array, filename: string) {
  const buffer = new ArrayBuffer(data.byteLength);
  new Uint8Array(buffer).set(data);
  const blob = new Blob([buffer], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export default function App() {
  const fileInputId = useId();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const addFiles = useCallback((list: FileList | null) => {
    if (!list?.length) return;
    setFiles((prev) => [...prev, ...Array.from(list)]);
    setError(null);
    setStatus(null);
  }, []);

  const onFileInputChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      addFiles(event.target.files);
      event.target.value = "";
    },
    [addFiles],
  );

  const removeAt = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
    setStatus(null);
  }, []);

  const clearAll = useCallback(() => {
    setFiles([]);
    setError(null);
    setStatus(null);
  }, []);

  const merge = useCallback(async () => {
    setError(null);
    setStatus(null);
    setBusy(true);
    try {
      const bytes = await mergePdfFiles(files);
      downloadBytes(bytes, "merged.pdf");
      setStatus("Merged successfully. Your download should start shortly.");
    } catch (e) {
      const msg =
        e instanceof Error
          ? e.message
          : "Merge failed. The file may be corrupt or password-protected.";
      setError(msg);
    } finally {
      setBusy(false);
    }
  }, [files]);

  return (
    <div className="app">
      <header className="hero">
        <p className="eyebrow">Browser tools</p>
        <h1 className="title">PDF Merger</h1>
        <p className="subtitle">
          Merge PDFs privately on your device—files never leave your browser.
        </p>

        <section className="merge-tools" aria-label="Merge PDF files">
          <div className="merge-toolbar">
            <label className="sr-only" htmlFor={fileInputId}>
              Add PDF files
            </label>
            <input
              id={fileInputId}
              ref={fileInputRef}
              className="visually-hidden-input"
              type="file"
              accept="application/pdf,.pdf"
              multiple
              onChange={onFileInputChange}
              disabled={busy}
            />
            <button
              type="button"
              className="btn btn-secondary"
              disabled={busy}
              onClick={() => fileInputRef.current?.click()}
            >
              Add PDFs
            </button>
            <button type="button" className="btn btn-secondary" disabled={busy || files.length === 0} onClick={clearAll}>
              Clear all
            </button>
            <button
              type="button"
              className="btn btn-primary"
              disabled={busy || files.length < 1}
              onClick={() => void merge()}
            >
              {busy ? "Merging…" : "Merge & download"}
            </button>
          </div>

          {files.length > 0 && (
            <ol className="merge-file-list">
              {files.map((file, index) => (
                <li key={`${file.name}-${file.size}-${file.lastModified}-${index}`} className="merge-file-row">
                  <span className="merge-file-order">{index + 1}.</span>
                  <span className="merge-file-name">{file.name}</span>
                  <button
                    type="button"
                    className="btn btn-ghost"
                    disabled={busy}
                    onClick={() => removeAt(index)}
                    aria-label={`Remove ${file.name}`}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ol>
          )}

          {error ? (
            <p className="merge-feedback merge-feedback-error" role="alert">
              {error}
            </p>
          ) : null}
          {status ? (
            <p className="merge-feedback merge-feedback-ok" role="status">
              {status}
            </p>
          ) : null}
        </section>
      </header>
    </div>
  );
}
