import { useEffect, useState } from "react";
import FaqView from "./FaqView";
import MergeView from "./MergeView";
import PrivacyView from "./PrivacyView";
import TermsView from "./TermsView";
import { hashForView, type AppView, viewFromHash } from "./routes";
import { SITE_REPO_URL } from "./site";

const DOCUMENT_TITLES: Record<AppView, string> = {
  merge: "PDF Merger — Merge PDFs privately in your browser",
  faq: "FAQ — PDF Merger",
  privacy: "Privacy Policy — PDF Merger",
  terms: "Terms of Use — PDF Merger",
};

function normalizeHashOnce() {
  const { hash } = window.location;
  if (hash === "" || hash === "#") {
    window.history.replaceState(
      null,
      "",
      `${window.location.pathname}${window.location.search}#/`,
    );
  }
}

function SiteHeader({ view }: { view: AppView }) {
  return (
    <header className="site-header">
      <div className="site-header-inner">
        <a className="site-brand" href={hashForView("merge")}>
          PDF Merger
        </a>
        <nav className="site-nav" aria-label="Primary">
          <a
            className="site-nav-link"
            href={hashForView("merge")}
            aria-current={view === "merge" ? "page" : undefined}
          >
            Merge
          </a>
          <a
            className="site-nav-link"
            href={hashForView("faq")}
            aria-current={view === "faq" ? "page" : undefined}
          >
            FAQ
          </a>
          <a
            className="site-nav-link"
            href={hashForView("privacy")}
            aria-current={view === "privacy" ? "page" : undefined}
          >
            Privacy
          </a>
          <a
            className="site-nav-link"
            href={hashForView("terms")}
            aria-current={view === "terms" ? "page" : undefined}
          >
            Terms
          </a>
        </nav>
      </div>
    </header>
  );
}

export default function App() {
  const [view, setView] = useState<AppView>(() => viewFromHash(window.location.hash));

  useEffect(() => {
    normalizeHashOnce();
    const onHashChange = () => setView(viewFromHash(window.location.hash));
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  useEffect(() => {
    document.title = DOCUMENT_TITLES[view];
  }, [view]);

  const year = new Date().getFullYear();

  return (
    <div className="layout">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <SiteHeader view={view} />
      <main id="main-content" className="main" tabIndex={-1}>
        {view === "merge" ? <MergeView /> : null}
        {view === "faq" ? <FaqView /> : null}
        {view === "privacy" ? <PrivacyView /> : null}
        {view === "terms" ? <TermsView /> : null}
      </main>
      <footer className="site-footer">
        <div className="site-footer-inner">
          <p className="site-footer-line">
            © {year} PDF Merger. Merge PDFs in your browser; files stay on your device.
          </p>
          <p className="site-footer-line site-footer-links">
            <a href={SITE_REPO_URL} rel="noopener noreferrer" target="_blank">
              Source on GitHub
            </a>
            <span aria-hidden="true"> · </span>
            <a href={hashForView("privacy")}>Privacy</a>
            <span aria-hidden="true"> · </span>
            <a href={hashForView("terms")}>Terms</a>
            <span aria-hidden="true"> · </span>
            <a href={hashForView("faq")}>FAQ</a>
          </p>
        </div>
      </footer>
    </div>
  );
}
