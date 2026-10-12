"""Render findings as terminal text or Markdown."""
from __future__ import annotations

from .checks import FAIL, WARN, INFO, Finding

ICON = {FAIL: "❌", WARN: "⚠️", INFO: "ℹ️"}
LABEL = {FAIL: "严重", WARN: "建议修改", INFO: "提示"}


def render_terminal(findings: list[Finding], score_: int, grade: str) -> str:
    lines = [f"\nmanulint 检查完成  |  得分 {score_}/100  |  {grade}", "-" * 56]
    for f in findings:
        lines.append(f"{ICON[f.severity]} [{LABEL[f.severity]}] {f.message}")
        if f.evidence:
            lines.append(f"    ↳ {f.evidence}")
    lines.append("-" * 56)
    lines.append(f"共 {len(findings)} 项："
                 f"{sum(1 for f in findings if f.severity == FAIL)} 严重 / "
                 f"{sum(1 for f in findings if f.severity == WARN)} 建议修改 / "
                 f"{sum(1 for f in findings if f.severity == INFO)} 提示")
    return "\n".join(lines)


CTA = ("---\n\n> 📝 **需要人工深度润色？**\n>\n"
       "> AI 能改语法，但看不懂片子、做不了临床判断。\n"
       "> 资深医学影像科医生提供医学论文润色与投稿前把关服务。\n"
       "> 👉 {cta_url}\n")


def render_markdown(findings: list[Finding], score_: int, grade: str,
                    source: str, cta_url: str = "") -> str:
    lines = [f"# manulint 检查报告", "", f"稿件：`{source}`",
             f"得分：**{score_}/100** —— {grade}", "",
             "| 级别 | 检查项 | 问题 | 依据 |",
             "|---|---|---|---|"]
    for f in findings:
        ev = f.evidence.replace("|", "\\|").replace("\n", " ") if f.evidence else ""
        lines.append(f"| {ICON[f.severity]} {LABEL[f.severity]} | {f.check} | {f.message} | {ev} |")
    lines += ["",
              "> 注：本工具为规则式自查，不能替代同行评议与期刊的具体要求，投稿前请核对目标期刊《作者指南》。",
              ""]
    if cta_url:
        lines.append(CTA.format(cta_url=cta_url))
    return "\n".join(lines)
