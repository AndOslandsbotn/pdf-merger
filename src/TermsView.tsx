import { SITE_REPO_URL } from "./site";

export default function TermsView() {
  return (
    <article className="content-page prose">
      <h1>Terms of use</h1>
      <p>
        <strong>Last updated:</strong> May 7, 2026. By using this website, you agree to these terms. If
        you disagree, do not use the site.
      </p>

      <h2>The service</h2>
      <p>
        The site provides a free, browser-based PDF merging utility &quot;as is.&quot; Features may
        change or be removed without notice.
      </p>

      <h2>No warranty</h2>
      <p>
        We disclaim all warranties to the fullest extent permitted by law. We do not guarantee that the
        tool will be error-free, uninterrupted, or suitable for any particular purpose. You use the tool
        at your own risk.
      </p>

      <h2>Your responsibilities</h2>
      <p>
        You are responsible for your files, backups, and compliance with applicable laws. Do not use the
        tool to infringe others&apos; rights or to process unlawful content. You are responsible for
        reviewing the merged output before relying on it.
      </p>

      <h2>Limitation of liability</h2>
      <p>
        To the fullest extent permitted by law, we are not liable for any indirect, incidental, special,
        consequential, or punitive damages, or any loss of data, profits, or goodwill, arising from your
        use of the site.
      </p>

      <h2>Contact</h2>
      <p>
        For questions, use{" "}
        <a href={SITE_REPO_URL} rel="noopener noreferrer" target="_blank">
          the project repository
        </a>
        .
      </p>
    </article>
  );
}
