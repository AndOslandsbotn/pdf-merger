export default function FaqView() {
  return (
    <article className="content-page prose">
      <h1>FAQ &amp; how it works</h1>
      <p>
        This page explains how the PDF merger works, what stays private, and what limits to expect in
        your browser.
      </p>

      <h2>Is my data private?</h2>
      <p>
        Yes. Merging runs entirely in your browser using JavaScript. Your PDFs are not uploaded to our
        servers—we do not operate a merge API. The site is served as static files (for example on{" "}
        <a href="https://pages.github.com/" rel="noopener noreferrer" target="_blank">
          GitHub Pages
        </a>
        ), which only hosts HTML, scripts, and assets.
      </p>

      <h2>How do I merge files?</h2>
      <p>
        Go to <a href="#/">Merge</a>, tap <strong>Add PDFs</strong>, choose PDFs in the order you want
        them to appear in the combined document, then use <strong>Merge &amp; download</strong>. You can
        remove files from the list or clear the list before merging.
      </p>

      <h2>Are there size or performance limits?</h2>
      <p>
        Very large PDFs or many files can exhaust available memory in the tab or make the merge slow.
        If merging fails, try fewer files or smaller documents, use a more powerful device, or merge in
        batches.
      </p>

      <h2>Do password-protected or encrypted PDFs work?</h2>
      <p>
        Password-protected or encrypted PDFs may fail to load. Remove the password in another tool
        first, then merge here.
      </p>

      <h2>Which browsers are supported?</h2>
      <p>
        Recent versions of Chrome, Firefox, Safari, and Edge generally work. Enable JavaScript and
        allow downloads from this site so the merged file can save.
      </p>
    </article>
  );
}
