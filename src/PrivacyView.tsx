import { SITE_REPO_URL } from "./site";

export default function PrivacyView() {
  return (
    <article className="content-page prose">
      <h1>Privacy policy</h1>
      <p>
        <strong>Last updated:</strong> May 7, 2026. This policy describes how this website handles
        information. We keep it accurate for a static, browser-based PDF tool; update this page if you
        change hosting, analytics, or advertising.
      </p>

      <h2>What this site does</h2>
      <p>
        PDF Merger lets you combine PDF files <strong>in your web browser</strong>. Processing happens on
        your device; PDF contents are not sent to us for merging because there is no merge backend.
      </p>

      <h2>What we collect</h2>
      <p>
        We do not operate accounts or a merge server for this web app. We may receive standard technical
        data that hosting providers or CDNs log automatically (for example IP address, User-Agent, and
        timestamps) depending on where the site is hosted.
      </p>

      <h2>Cookies and similar technologies</h2>
      <p>
        The core merging tool does not require you to log in. If we add analytics or advertising (such as{" "}
        <a href="https://www.google.com/adsense" rel="noopener noreferrer" target="_blank">
          Google AdSense
        </a>
        ), those services may set or read cookies or use similar storage. When that is enabled, we will
        update this policy and use consent tools where required (for example in the EEA and UK) so you
        can make informed choices.
      </p>

      <h2>Children</h2>
      <p>This site is not directed at children under 13. Do not use the tool if you are under 13.</p>

      <h2>Third-party links</h2>
      <p>
        This site may link to third parties (for example hosting or program policies). Their practices are
        governed by their own terms and policies.
      </p>

      <h2>Contact</h2>
      <p>
        Questions about this policy: open an issue on{" "}
        <a href={SITE_REPO_URL} rel="noopener noreferrer" target="_blank">
          the project repository
        </a>
        .
      </p>
    </article>
  );
}
