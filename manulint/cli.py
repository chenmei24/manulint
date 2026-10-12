"""Command-line interface: manulint paper.docx [--md report.md]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .checks import run_all, score
from .readers import read_manuscript
from .report import render_terminal, render_markdown


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="manulint",
        description="投稿前自查：发现可能导致直接拒稿（desk rejection）的问题")
    ap.add_argument("manuscript", help="稿件文件（.docx / .md / .txt）")
    ap.add_argument("--md", metavar="OUT.md",
                    help="同时输出 Markdown 报告到文件")
    ap.add_argument("--cta", default="",
                    help="报告末尾的润色服务链接（引流用）")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = ap.parse_args(argv)

    src = Path(args.manuscript)
    if not src.is_file():
        print(f"错误：找不到文件 {src}", file=sys.stderr)
        return 2
    try:
        m = read_manuscript(src)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 2

    findings = run_all(m)
    s, grade = score(findings)
    print(render_terminal(findings, s, grade))

    if args.md:
        Path(args.md).write_text(
            render_markdown(findings, s, grade, src.name, args.cta),
            encoding="utf-8")
        print(f"\nMarkdown 报告已保存：{args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
