#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

from pypdf import PdfWriter


def _file_dialog_initialdir() -> str | None:
    """Prefer Windows drives when running under WSL so picks open under /mnt/c/..."""
    for candidate in ("/mnt/c/Users", os.path.expanduser("~")):
        if os.path.isdir(candidate):
            return candidate
    return None


def merge_pdf_files(output_path: str, input_paths: list[str]) -> None:
    writer = PdfWriter()
    try:
        for path in input_paths:
            writer.append(path)
        writer.write(output_path)
    finally:
        writer.close()


def _format_bytes(num_bytes: int) -> str:
    return f"{num_bytes / (1024 * 1024):.2f} MB"


def _populate_merge_tab(
    parent,
    fd_opts: dict,
) -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox

    paths: list[str] = []

    hint = tk.Label(
        parent,
        text="Add PDFs (top to bottom = merge order), then click “Merge PDFs…”.",
        wraplength=600,
        justify=tk.LEFT,
    )
    hint.pack(anchor=tk.W, padx=8, pady=(8, 4))

    list_frame = tk.Frame(parent)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

    list_scroll = tk.Scrollbar(list_frame)
    list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(
        list_frame,
        selectmode=tk.EXTENDED,
        yscrollcommand=list_scroll.set,
        font=("TkFixedFont",),
    )
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    list_scroll.config(command=listbox.yview)

    def refresh_listbox() -> None:
        listbox.delete(0, tk.END)
        for i, p in enumerate(paths):
            listbox.insert(tk.END, f"{i + 1:2}. {p}")

    def add_pdfs() -> None:
        picked = filedialog.askopenfilenames(
            title="Select PDF files to add",
            filetypes=[("PDF files", "*.pdf")],
            **fd_opts,
        )
        if picked:
            paths.extend(picked)
            refresh_listbox()

    def remove_selected() -> None:
        sel = list(listbox.curselection())
        if not sel:
            return
        for i in reversed(sel):
            del paths[i]
        refresh_listbox()

    def move_up() -> None:
        sel = listbox.curselection()
        if len(sel) != 1:
            return
        i = int(sel[0])
        if i <= 0:
            return
        paths[i - 1], paths[i] = paths[i], paths[i - 1]
        refresh_listbox()
        listbox.selection_set(i - 1)
        listbox.see(i - 1)

    def move_down() -> None:
        sel = listbox.curselection()
        if len(sel) != 1:
            return
        i = int(sel[0])
        if i >= len(paths) - 1:
            return
        paths[i], paths[i + 1] = paths[i + 1], paths[i]
        refresh_listbox()
        listbox.selection_set(i + 1)
        listbox.see(i + 1)

    row = tk.Frame(parent)
    row.pack(fill=tk.X, padx=8, pady=4)

    tk.Button(row, text="Add PDFs…", command=add_pdfs).pack(side=tk.LEFT, padx=(0, 4))
    tk.Button(row, text="Remove", command=remove_selected).pack(side=tk.LEFT, padx=4)
    tk.Button(row, text="↑", width=3, command=move_up).pack(side=tk.LEFT, padx=(12, 2))
    tk.Button(row, text="↓", width=3, command=move_down).pack(side=tk.LEFT, padx=2)

    def do_merge() -> None:
        if not paths:
            messagebox.showwarning("No PDFs", "Add at least one PDF first.")
            return
        output = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save merged PDF as",
            **fd_opts,
        )
        if not output:
            return
        try:
            merge_pdf_files(output, list(paths))
            messagebox.showinfo("Success", f"Merged PDF saved to:\n{output}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(
        parent,
        text="Merge PDFs…",
        height=2,
        command=do_merge,
    ).pack(fill=tk.X, padx=8, pady=(8, 8))


def _populate_compress_tab(parent, fd_opts: dict) -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from tkinter import ttk

    import compress as compress_pdf

    src: dict[str, str | None] = {"path": None}

    tk.Label(
        parent,
        text=(
            "Pick one PDF, choose quality, then save a smaller copy. "
            "Requires Ghostscript (gs). Optional max size retries with a stronger preset once."
        ),
        wraplength=600,
        justify=tk.LEFT,
    ).pack(anchor=tk.W, padx=8, pady=(8, 4))

    path_label = tk.Label(
        parent,
        text="(no PDF selected)",
        wraplength=600,
        justify=tk.LEFT,
        fg="gray",
    )
    path_label.pack(anchor=tk.W, padx=8, pady=4)

    def choose_pdf() -> None:
        f = filedialog.askopenfilename(
            title="PDF to compress",
            filetypes=[("PDF files", "*.pdf")],
            **fd_opts,
        )
        if f:
            src["path"] = f
            path_label.config(text=f, fg="black")

    tk.Button(parent, text="Choose PDF…", command=choose_pdf).pack(
        anchor=tk.W, padx=8, pady=(0, 8)
    )

    opt_row = tk.Frame(parent)
    opt_row.pack(fill=tk.X, padx=8, pady=4)
    tk.Label(opt_row, text="Quality preset:").pack(side=tk.LEFT, padx=(0, 8))
    preset_var = tk.StringVar(value="ebook")
    ttk.Combobox(
        opt_row,
        textvariable=preset_var,
        values=list(compress_pdf.PRESETS),
        state="readonly",
        width=12,
    ).pack(side=tk.LEFT)

    max_row = tk.Frame(parent)
    max_row.pack(fill=tk.X, padx=8, pady=4)
    tk.Label(max_row, text="Max output size (MiB, optional):").pack(side=tk.LEFT, padx=(0, 8))
    max_mb_var = tk.StringVar(value="")
    tk.Entry(max_row, textvariable=max_mb_var, width=10).pack(side=tk.LEFT)

    def do_compress() -> None:
        p = src["path"]
        if not p:
            messagebox.showwarning("No file", "Choose a PDF first.")
            return

        inp = Path(p).expanduser().resolve()
        initial = f"{inp.stem}-compressed.pdf"
        out = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save compressed PDF as",
            initialfile=initial,
            **fd_opts,
        )
        if not out:
            return

        outp = Path(out).expanduser().resolve()
        if outp.resolve() == inp.resolve():
            messagebox.showerror(
                "Output",
                "Output file must differ from the input file.",
            )
            return

        raw_max = max_mb_var.get().strip()
        max_mb: float | None
        try:
            max_mb = float(raw_max) if raw_max else None
        except ValueError:
            messagebox.showerror("Invalid input", "Max size must be a number (MiB) or blank.")
            return

        preset = preset_var.get()
        try:
            if max_mb is None:
                before, after = compress_pdf.compress_pdf_file(inp, outp, preset)
                preset_used = preset
            else:
                before, after, preset_used = compress_pdf.compress_with_max_mb_retry(
                    inp,
                    outp,
                    preset,
                    max_mb,
                )
        except RuntimeError as e:
            messagebox.showerror("Compression failed", str(e))
            return

        pct = 100.0 * (1.0 - after / before) if before else 0.0
        messagebox.showinfo(
            "Success",
            f"Saved:\n{outp}\n\n"
            f"{_format_bytes(before)} → {_format_bytes(after)} ({pct:+.1f}%)\n"
            f"Preset: {preset_used}",
        )

    tk.Button(
        parent,
        text="Compress and save…",
        height=2,
        command=do_compress,
    ).pack(fill=tk.X, padx=8, pady=(16, 8))


def merge_pdfs_gui() -> None:
    import tkinter as tk
    from tkinter import ttk

    fd_root = _file_dialog_initialdir()
    fd_opts = {"initialdir": fd_root} if fd_root else {}

    root = tk.Tk()
    root.title("PDF Merge & Compress")
    root.minsize(520, 400)
    root.geometry("660x460")

    nb = ttk.Notebook(root)
    nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    merge_tab = tk.Frame(nb)
    compress_tab = tk.Frame(nb)
    nb.add(merge_tab, text="Merge PDFs")
    nb.add(compress_tab, text="Compress PDF")

    _populate_merge_tab(merge_tab, fd_opts)
    _populate_compress_tab(compress_tab, fd_opts)

    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge and compress PDFs. No arguments: GUI with Merge and Compress tabs (requires python3-tk and gs for compress).",
        epilog="WSL: Windows files are under /mnt/c/ (e.g. Desktop: /mnt/c/Users/<You>/Desktop).",
    )
    parser.add_argument(
        "output",
        nargs="?",
        help="Output PDF path (CLI mode). Omit to open the GUI.",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Input PDF files in order (CLI mode).",
    )
    args = parser.parse_args()

    if args.output is None:
        try:
            merge_pdfs_gui()
        except ModuleNotFoundError as e:
            if e.name == "tkinter":
                print(
                    "GUI needs Tk for Python. On Ubuntu/WSL: sudo apt install python3-tk\n"
                    "Or merge from the terminal (WSL: use /mnt/c/Users/... for Windows files):\n"
                    "  python main.py OUTPUT.pdf FIRST.pdf SECOND.pdf ...",
                    file=sys.stderr,
                )
                sys.exit(1)
            raise
        return

    if not args.inputs:
        parser.error("CLI mode needs at least one input PDF after the output path.")

    try:
        merge_pdf_files(args.output, args.inputs)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
