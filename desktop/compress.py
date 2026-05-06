#!/usr/bin/env python3
"""
Compress PDFs via Ghostscript (gs). Target file size is best-effort; results depend on source PDF.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PRESETS = ("screen", "ebook", "printer", "prepress")

# Stronger compression = smaller files (typical). Used for --max-mb escalation (one step).
NEXT_STRONGER: dict[str, str | None] = {
    "prepress": "printer",
    "printer": "ebook",
    "ebook": "screen",
    "screen": None,
}


def _windows_style_path_to_wsl(raw: str) -> str:
    """Turn C:\\Users\\foo\\x.pdf into /mnt/c/Users/foo/x.pdf when running under WSL/Linux."""
    s = raw.strip()
    if len(s) >= 2 and s[0].isalpha() and s[1] == ":":
        drive = s[0].lower()
        rest = s[2:].replace("\\", "/")
        rest = rest.lstrip("/")
        return f"/mnt/{drive}/{rest}"
    return s


def _path_from_cli(raw: str) -> Path:
    """Path() as given, or normalized from a Windows-style string the user pasted in WSL."""
    normalized = _windows_style_path_to_wsl(raw)
    return Path(normalized)


def _format_mb(num_bytes: int) -> str:
    return f"{num_bytes / (1024 * 1024):.2f} MB"


def _file_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def _require_gs() -> str:
    gs = shutil.which("gs")
    if not gs:
        print(
            "Ghostscript (gs) not found on PATH.\n"
            "Install on Ubuntu/WSL: sudo apt install ghostscript",
            file=sys.stderr,
        )
        sys.exit(127)
    return gs


def _default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}-compressed.pdf")


def run_gs(
    gs_bin: str,
    input_pdf: Path,
    output_pdf: Path,
    preset: str,
) -> None:
    if preset not in PRESETS:
        raise ValueError(f"invalid preset {preset!r}")
    settings = f"/{preset}"
    cmd = [
        gs_bin,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={settings}",
        "-dNOPAUSE",
        "-dBATCH",
        "-dQUIET",
        f"-sOutputFile={output_pdf.resolve()}",
        str(input_pdf.resolve()),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        msg = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(
            f"Ghostscript failed (exit {result.returncode}):\n{msg}",
        )


def compress_pdf_file(
    input_pdf: Path,
    output_pdf: Path,
    preset: str,
) -> tuple[int, int]:
    """
    Run Ghostscript once. Returns (input_bytes, output_bytes).
    Raises RuntimeError if gs is missing or the run fails.
    """
    gs_bin = shutil.which("gs")
    if not gs_bin:
        raise RuntimeError(
            "Ghostscript (gs) not found on PATH.\n"
            "Install on Ubuntu/WSL: sudo apt install ghostscript",
        )
    input_pdf = input_pdf.expanduser().resolve()
    output_pdf = output_pdf.expanduser().resolve()
    if not input_pdf.is_file():
        raise RuntimeError(f"Not a file: {input_pdf}")
    before = input_pdf.stat().st_size
    run_gs(gs_bin, input_pdf, output_pdf, preset)
    after = output_pdf.stat().st_size
    return before, after


def compress_with_max_mb_retry(
    input_pdf: Path,
    output_pdf: Path,
    initial_preset: str,
    max_mb: float | None,
) -> tuple[int, int, str]:
    """
    Compress; if max_mb given and output still too large, retry once with NEXT_STRONGER preset.
    Returns (before_bytes, after_bytes, preset_used).
    """
    preset = initial_preset
    before, after = compress_pdf_file(input_pdf, output_pdf, preset)

    max_bytes = int(max_mb * 1024 * 1024) if max_mb is not None else None
    if max_bytes is None or after <= max_bytes:
        return before, after, preset

    stronger = NEXT_STRONGER[preset]
    if stronger is None:
        raise RuntimeError(
            f"Output still {_file_mb(output_pdf):.2f} MiB (limit {max_mb} MiB). "
            "already using strongest preset (screen)."
        )

    compress_pdf_file(input_pdf, output_pdf, stronger)
    after = output_pdf.stat().st_size
    if after > max_bytes:
        raise RuntimeError(
            f"Output still {_file_mb(output_pdf):.2f} MiB (limit {max_mb} MiB). "
            "Try processing images externally or splitting the PDF."
        )
    return before, after, stronger


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compress a PDF using Ghostscript (best-effort; depends on source file).",
        epilog=(
            "There is no guarantee a given PDF will reach --max-mb; escalation retries once "
            "with a stronger preset. Scanned/image-heavy PDFs may need stronger presets manually.\n"
            "WSL: Paths may contain spaces — either quote the whole path, or omit quotes and all "
            "words after flags are joined into one input path (Bash splits on spaces otherwise). "
            "Windows paths (C:\\\\Users\\\\...) and /mnt/c/... both work."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output PDF (default: <name>-compressed.pdf next to input); quote if path has spaces",
    )
    parser.add_argument(
        "--preset",
        choices=PRESETS,
        default="ebook",
        help="Ghostscript PDFSETTINGS profile (default: ebook)",
    )
    parser.add_argument(
        "--max-mb",
        type=float,
        default=None,
        metavar="N",
        help="If set, exit with error if output still exceeds N MiB; may retry once with a stronger preset",
    )
    parser.add_argument(
        "input_parts",
        nargs="+",
        metavar="INPUT",
        help="Input PDF — one path; multiple words without quotes are treated as one path with spaces between",
    )
    args = parser.parse_args()

    joined_input = " ".join(args.input_parts)
    input_path = _path_from_cli(joined_input).expanduser().resolve()
    if not input_path.is_file():
        hint = ""
        if input_path.suffix.lower() != ".pdf":
            hint = " (did you forget the .pdf extension?)"
        print(f"Not a file: {input_path}{hint}", file=sys.stderr)
        print(
            "Tip: use one path only (quote it, or let the tool join words after options). "
            "In Bash, Windows paths with backslashes are easiest as /mnt/c/Users/... or C:/Users/.../file.pdf",
            file=sys.stderr,
        )
        sys.exit(2)

    output_path = (
        _path_from_cli(args.output).expanduser().resolve()
        if args.output
        else _default_output_path(input_path)
    )
    if output_path.resolve() == input_path.resolve():
        print("Output path must differ from input path.", file=sys.stderr)
        sys.exit(2)

    _require_gs()

    preset = args.preset
    print(f"Input:  {input_path} ({_format_mb(input_path.stat().st_size)})")
    print(f"Preset: {preset}")
    try:
        before, after, preset_used = compress_with_max_mb_retry(
            input_path,
            output_path,
            preset,
            args.max_mb,
        )
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    print(f"Preset used: {preset_used}")
    print(f"Output: {output_path} ({_format_mb(after)})")

    savings = 100.0 * (1 - after / before) if before else 0.0
    print(f"Change: {savings:+.1f}% size vs input")


if __name__ == "__main__":
    main()
