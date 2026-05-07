import { PDFDocument } from "pdf-lib";

/**
 * Merges PDFs in the given order (all pages from file[0], then file[1], …).
 * Runs entirely in the browser; files are not uploaded.
 */
export async function mergePdfFiles(files: File[]): Promise<Uint8Array> {
  if (files.length === 0) {
    throw new Error("Select at least one PDF to merge.");
  }

  const merged = await PDFDocument.create();

  for (const file of files) {
    const bytes = await file.arrayBuffer();
    const doc = await PDFDocument.load(bytes);
    const indices = doc.getPageIndices();
    const pages = await merged.copyPages(doc, indices);
    pages.forEach((page) => merged.addPage(page));
  }

  return merged.save();
}
