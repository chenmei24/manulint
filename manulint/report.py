"""Render local findings without publication-readiness claims."""
from __future__ import annotations

import html
import re

from .checks import FAIL, WARN, INFO, Finding

ICON = {FAIL: "[FLAG]", WARN: "[WARN]", INFO: "[INFO]"}
LABEL = {FAIL: "Flagged rule", WARN: "Warning", INFO: "Information"}
LIMITATION = ("Heuristic rule checks only. The score is not validated and does not measure "
              "publication readiness, scientific quality, or ethical adequacy. Verify the target journal's author instructions.")


def _plain(value: str) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", str(value)).replace("\r", " ")


def _escape(value: str) -> str:
    value = html.escape(_plain(value).replace("\n", " "), quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+.!|])", r"\\\1", value)


def render_terminal(findings: list[Finding], score_: int, grade: str) -> str:
    lines = [f"\nmanulint rule check | score {score_}/100 | {_plain(grade)}", "-" * 56]
    for finding in findings:
        lines.append(f"{ICON[finding.severity]} {_plain(finding.message)}")
        if finding.evidence:
            lines.append(f"    Evidence: {_plain(finding.evidence)}")
    lines += ["-" * 56, LIMITATION]
    return "\n".join(lines)


def render_markdown(findings: list[Finding], score_: int, grade: str,
                    source: str, cta_url: str = "", profile: str = "") -> str:
    lines = ["# manulint rule-check report", "", f"Manuscript: {_escape(source)}", "",
             f"Rule score: **{score_}/100** — {_escape(grade)}", ""]
    if profile:
        lines += [f"Profile: {_escape(profile)}", ""]
    lines += ["| Level | Check | Rule | Finding | Evidence |",
              "|---|---|---|---|---|"]
    for finding in findings:
        fields = (LABEL[finding.severity], finding.check, finding.rule, finding.message, finding.evidence)
        lines.append("| " + " | ".join(_escape(value) for value in fields) + " |")
    lines += ["", "> " + LIMITATION, ""]
    if cta_url:
        lines += ["Optional service link: " + _escape(cta_url), ""]
    return "\n".join(lines)
