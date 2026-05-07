# PDF Merger

Merge PDFs in the browser (GitHub Pages) and optional local desktop tools (Python).

## Web app (GitHub Pages)

Static site built with Vite and React. PDF merging in the browser will be added incrementally.

```bash
npm install
npm run dev
```

Production build (output in `dist/`):

```bash
npm run build
```

For a project site at `https://<user>.github.io/pdf-merger/`, `vite.config.ts` sets `base: '/pdf-merger/'`. Change `base` to `'/'` if you use a custom domain or a user/org root site (`*.github.io`).

Enable **GitHub Pages** with the **GitHub Actions** source. The workflow `.github/workflows/pages.yml` builds and deploys `dist/`.

## Desktop (Python)


Local GUI/CLI tools using `pypdf` and optional Ghostscript for compression. Run from the `desktop/` directory:

```bash
cd desktop
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

PDF compression helper (requires `gs`):

```bash
python compress.py --help
```

Packaged helper scripts in `desktop/` (`pdf-merger`, `pdf-compress`) are optional; you can run the `.py` files directly.
