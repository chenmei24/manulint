"""Command-line interface: manulint paper.docx --md report.md."""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from . import __version__
from .checks import CheckConfig, run_all, score
from .readers import read_manuscript
from .report import render_terminal, render_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="manulint", description="Local heuristic checklist for manuscript reporting and formatting.")
    parser.add_argument("manuscript", help="Manuscript file (.docx / .md / .txt)")
    parser.add_argument("--md", metavar="OUT.md", help="Write a Markdown report")
    parser.add_argument("--article-type", choices=("original", "review", "case-report"), default="original",
                        help="Generic rule profile, not a journal template (default: original)")
    parser.add_argument("--language", choices=("en", "zh", "auto"), default="auto",
                        help="Manuscript language for punctuation/counting rules (default: auto)")
    parser.add_argument("--p-style", choices=("lower", "upper", "either"), default="either",
                        help="Journal's p/P style; either disables case warnings (default: either)")
    parser.add_argument("--cta", default="", help="Optional http(s) service URL included in the report")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)
    source = Path(args.manuscript)
    if not source.is_file():
        print(f"Input error: file not found: {source}", file=sys.stderr)
        return 2
    output = Path(args.md) if args.md else None
    same_source = output is not None and source.resolve() == output.resolve()
    if output is not None and output.exists():
        try:
            same_source = same_source or source.samefile(output)
        except OSError as exc:
            print(f"Output error: cannot inspect report path: {exc}", file=sys.stderr)
            return 2
    if same_source:
        print("Input error: report path must differ from manuscript path.", file=sys.stderr)
        return 2
    if args.cta:
        try:
            url = urlsplit(args.cta)
        except ValueError:
            print("Input error: --cta must be a valid http(s) URL.", file=sys.stderr)
            return 2
        if url.scheme not in ("http", "https") or not url.netloc or any(ch.isspace() for ch in args.cta):
            print("Input error: --cta must be a valid http(s) URL without whitespace.", file=sys.stderr)
            return 2
    config = CheckConfig(args.article_type, args.language, args.p_style)
    try:
        manuscript = read_manuscript(source)
        findings = run_all(manuscript, config)
    except (ValueError, OSError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    value, label = score(findings)
    print(render_terminal(findings, value, label))
    if args.md:
        profile = f"article_type={config.article_type}, language={config.language}, p_style={config.p_style}"
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=output.parent, prefix=".manulint-", suffix=".tmp", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(render_markdown(findings, value, label, source.name, args.cta, profile))
            os.replace(temporary, output)
        except OSError as exc:
            print(f"Output error: cannot write report: {exc}", file=sys.stderr)
            return 2
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        print(f"\nMarkdown report saved: {args.md}")
    # Exit 0 means the check ran, not that the manuscript passed validation.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
