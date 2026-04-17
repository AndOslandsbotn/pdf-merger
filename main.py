import argparse
import os
import sys

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


def merge_pdfs_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    fd_root = _file_dialog_initialdir()
    fd_opts = {"initialdir": fd_root} if fd_root else {}

    paths: list[str] = []

    root = tk.Tk()
    root.title("PDF Merger")
    root.minsize(520, 360)
    root.geometry("640x420")

    hint = tk.Label(
        root,
        text="Add PDFs (top to bottom = merge order), then click “Merge PDFs…”.",
        wraplength=600,
        justify=tk.LEFT,
    )
    hint.pack(anchor=tk.W, padx=8, pady=(8, 4))

    list_frame = tk.Frame(root)
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

    row = tk.Frame(root)
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
        root,
        text="Merge PDFs…",
        height=2,
        command=do_merge,
    ).pack(fill=tk.X, padx=8, pady=(8, 8))

    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge PDF files. Run with no arguments for a graphical picker (requires python3-tk).",
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
