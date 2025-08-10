#!/usr/bin/env python3
import os
import argparse
from pathlib import Path

def build_tree(startpath: Path, max_depth: int | None = None):
    lines = []
    skip_dirs = {"venv"}  # Add folder names here to skip their details

    def _walk(path: Path, prefix: str = "", depth: int = 0):
        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            return

        for i, entry in enumerate(entries):
            last = (i == len(entries) - 1)
            connector = "└── " if last else "├── "
            lines.append(prefix + connector + entry.name)

            if entry.is_dir():
                if entry.name in skip_dirs:
                    # Skip descending into these directories
                    continue

                extension = "    " if last else "│   "
                if max_depth is None or depth + 1 < max_depth:
                    _walk(entry, prefix + extension, depth + 1)

    root_name = startpath.name
    lines.append(f"{root_name}/")
    _walk(startpath)
    return lines

def main():
    p = argparse.ArgumentParser(description="Generate a tree view of a directory and save to file.")
    p.add_argument("-r", "--root", type=str, default=".", help="Root directory to inspect (default: current directory).")
    p.add_argument("-o", "--output", type=str, default="repo_structure.txt", help="Output filename (txt or md).")
    p.add_argument("-m", "--markdown", action="store_true", help="Wrap output in a Markdown code block (triple backticks).")
    p.add_argument("--max-depth", type=int, default=None, help="Maximum depth to traverse (optional).")
    args = p.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Error: root path does not exist: {root}")
        return

    lines = build_tree(root, max_depth=args.max_depth)

    out_path = Path(args.output)
    if args.markdown:
        content = "```\n" + "\n".join(lines) + "\n```\n"
    else:
        content = "\n".join(lines) + "\n"

    out_path.write_text(content, encoding="utf-8")
    print(f"Tree saved to: {out_path.resolve()}")
    print()
    print("Preview:")
    print("\n".join(lines[:50]) + ("\n... (truncated)" if len(lines) > 50 else ""))

if __name__ == "__main__":
    main()
