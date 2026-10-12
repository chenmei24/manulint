"""Rule-based pre-submission checks (heuristics, not peer review)."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .readers import Manuscript

FAIL = "fail"
WARN = "warn"
INFO = "info"


@dataclass
class Finding:
    severity: str
    check: str
    rule: str
    message: str
    evidence: str = ""


SECTION_PATTERNS = {
    "abstract": r"\babstract\b|摘要",
    "keywords": r"\bkey\s?words\b|关键词",
    "introduction": r"\bintroduction\b|引言|前言",
    "methods": r"\bmethods?\b|materials?\s+and\s+methods?|方法|材料与方法",
    "results": r"\bresults?\b|结果",
    "discussion": r"\bdiscussion\b|讨论",
    "conclusion": r"\bconclusions?\b|结论",
    "references": r"\breferences?\b|参考文献",
    "acknowledgments": r"\backnowledg(e)?ments?\b|致谢",
    "ethics": r"\bethics?\b|ethical|伦理",
    "conflict": r"\bconflict(s)?\s+of\s+interest\b|利益冲突",
    "funding": r"\bfunding\b|基金|资助",
    "data_availability": r"\bdata\s+availability\b|数据可用性",
}

REQUIRED_SECTIONS = ["abstract", "introduction", "methods",
                     "results", "discussion", "references"]
RECOMMENDED_SECTIONS = ["keywords", "ethics", "conflict",
                        "funding", "data_availability"]


def _section_lines(text):
    found = {}
    for i, raw in enumerate(text.splitlines()):
        line = raw.strip()
        if not line or len(line) > 80:
            continue
        low = line.lower()
        for sid, pat in SECTION_PATTERNS.items():
            if sid not in found and re.search(pat, low):
                if len(line.split()) <= 10:
                    found[sid] = i
    return found


def check_structure(m):
    secs = _section_lines(m.text)
    out = []
    for sid in REQUIRED_SECTIONS:
        if sid not in secs:
            out.append(Finding(FAIL, "structure", "missing-" + sid,
                               "未检测到[%s]章节，多数期刊要求完整的 IMRaD 结构" % sid))
    for sid in RECOMMENDED_SECTIONS:
        if sid not in secs:
            out.append(Finding(WARN, "structure", "missing-" + sid,
                               "未检测到[%s]，建议补充（期刊常要求）" % sid))
    if not out:
        out.append(Finding(INFO, "structure", "ok", "IMRaD 核心章节齐全"))
    return out


def check_ethics(m):
    t = m.text
    out = []
    has_irb = bool(re.search(r"ethics?\s*committee|institutional review board|\bIRB\b|伦理委员会", t, re.I))
    has_consent = bool(re.search(r"informed consent|知情同意", t, re.I))
    has_helsinki = bool(re.search(r"helsinki|赫尔辛基", t, re.I))
    if not has_irb:
        out.append(Finding(WARN, "ethics", "no-irb",
                           "未找到伦理审查（IRB/伦理委员会）声明，人体/动物研究投稿通常必填"))
    if not has_consent:
        out.append(Finding(WARN, "ethics", "no-consent",
                           "未找到知情同意声明；如为回顾性研究，请注明豁免情况"))
    if has_irb and not has_helsinki:
        out.append(Finding(INFO, "ethics", "no-helsinki",
                           "有伦理声明但未提及《赫尔辛基宣言》，部分期刊建议加上"))
    if not out:
        out.append(Finding(INFO, "ethics", "ok", "伦理相关声明齐全"))
    return out


P_ZERO = re.compile(r"[Pp]\s*=\s*0\.000\b")
P_CAPITAL = re.compile(r"\bP\s*[=<>]")
P_NOSPACE = re.compile(r"[Pp]=0\.\d+")
N_REPORTED = re.compile(r"\bn\s*=\s*\d+", re.I)
TEST_NAMED = re.compile(
    r"t[-\s]?test|chi[-\s]?square|ANOVA|ANCOVA|Mann-?Whitney|Wilcoxon|"
    r"Kruskal-?Wallis|regression|logistic|\bCox\b|Kaplan-?Meier|Fisher",
    re.I)
CI_REPORTED = re.compile(r"95\s?%\s?CI|confidence interval|置信区间", re.I)


def check_statistics(m):
    t = m.text
    out = []
    zeros = P_ZERO.findall(t)
    if zeros:
        out.append(Finding(FAIL, "statistics", "p-zero",
                           "发现 %d 处 p = 0.000，应写为 p < 0.001（p 值不可能恰为 0）" % len(zeros),
                           "; ".join(zeros[:3])))
    if P_CAPITAL.search(t):
        out.append(Finding(WARN, "statistics", "p-capital",
                           "p 值用了大写 P，规范写法是小写斜体 p"))
    if P_NOSPACE.search(t):
        out.append(Finding(WARN, "statistics", "p-nospace",
                           "p 值等号前后缺少空格，如 p=0.03 应写为 p = 0.03"))
    if not N_REPORTED.search(t):
        out.append(Finding(WARN, "statistics", "no-n",
                           "未找到样本量表述（n = …），方法部分应明确每组样本量"))
    if not TEST_NAMED.search(t):
        out.append(Finding(WARN, "statistics", "no-test",
                           "未识别出具体统计检验方法（t 检验/卡方/ANOVA/回归等），方法部分应写明"))
    if re.search(r"[Pp]\s*[=<>]", t) and not CI_REPORTED.search(t):
        out.append(Finding(WARN, "statistics", "no-ci",
                           "报告了 p 值但未见置信区间（CI）/效应量，建议补充（CONSORT/STROBE 推荐）"))
    if not out:
        out.append(Finding(INFO, "statistics", "ok", "统计表述基本规范"))
    return out


def check_figures(m):
    out = []
    if not m.figures:
        return [Finding(INFO, "figures", "none-found",
                        "未检测到内嵌图片（或图片在外部文件中），跳过分辨率检查")]
    for fig in m.figures:
        w, h = fig.image.size
        if fig.width_in:
            dpi = w / fig.width_in
            if dpi < 150:
                out.append(Finding(FAIL, "figures", "low-dpi",
                                   "图片 %s 有效分辨率约 %.0f dpi，远低于印刷要求的 300 dpi" % (fig.name, dpi),
                                   "%dx%dpx，显示宽度 %.1f 英寸" % (w, h, fig.width_in)))
            elif dpi < 300:
                out.append(Finding(WARN, "figures", "low-dpi",
                                   "图片 %s 有效分辨率约 %.0f dpi，建议不低于 300 dpi" % (fig.name, dpi),
                                   "%dx%dpx，显示宽度 %.1f 英寸" % (w, h, fig.width_in)))
            else:
                out.append(Finding(INFO, "figures", "dpi-ok",
                                   "图片 %s 分辨率约 %.0f dpi，符合要求" % (fig.name, dpi)))
        else:
            out.append(Finding(INFO, "figures", "unknown-size",
                               "图片 %s（%dx%dpx）无法判断版面显示尺寸，请自行确认不低于 300 dpi" % (fig.name, w, h)))
    return out


def check_references(m):
    out = []
    secs = _section_lines(m.text)
    if "references" not in secs:
        return out
    lines = m.text.splitlines()
    ref_text = "\n".join(lines[secs["references"]:])
    nums = []
    for raw in ref_text.splitlines():
        mm = re.match(r"\s*[\[\(]?(\d+)[\.\)\]\]]\s+\S", raw)
        if mm:
            nums.append(int(mm.group(1)))
    if not nums:
        out.append(Finding(INFO, "references", "unparsed",
                           "参考文献为非编号格式（如 Author-Year），跳过编号连续性检查"))
        return out
    missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
    if missing:
        out.append(Finding(FAIL, "references", "number-gap",
                           "参考文献编号不连续，缺失：%s" % missing[:10],
                           "共识别 %d 条" % len(nums)))
    else:
        out.append(Finding(INFO, "references", "ok",
                           "参考文献编号连续，共 %d 条" % len(nums)))
    seen = set()
    dups = 0
    for raw in ref_text.splitlines():
        s = raw.strip().lower()
        if len(s) > 40:
            if s in seen:
                dups += 1
            seen.add(s)
    if dups:
        out.append(Finding(WARN, "references", "duplicates",
                           "发现 %d 条疑似重复的参考文献" % dups))
    return out


CJK_PUNCT = re.compile(r"[，。；：、（）《》]")


def check_language(m):
    from collections import Counter
    t = m.text
    out = []
    cjk = CJK_PUNCT.findall(t)
    if cjk:
        common = "".join(c for c, _ in Counter(cjk).most_common(3))
        out.append(Finding(WARN, "language", "cjk-punct",
                           "英文稿中发现 %d 个中文标点（如%s），请替换为英文标点" % (len(cjk), common)))
    doubles = len(re.findall(r"  ", t))
    if doubles > 10:
        out.append(Finding(WARN, "language", "double-space",
                           "发现 %d 处连续双空格，建议全文清理" % doubles))
    n_fig = len(re.findall(r"\bFig\.", t))
    n_figure = len(re.findall(r"\bFigure\b", t))
    if n_fig and n_figure:
        out.append(Finding(WARN, "language", "fig-mixed",
                           "Fig.（%d 次）与 Figure（%d 次）混用，请全文统一" % (n_fig, n_figure)))
    if not out:
        out.append(Finding(INFO, "language", "ok", "未发现明显的标点/格式混用问题"))
    return out


def check_meta(m):
    out = []
    lines = [ln.strip() for ln in m.text.splitlines() if ln.strip()]
    if not lines:
        return [Finding(FAIL, "meta", "empty", "文档为空或无法提取文本")]
    title = lines[0]
    nw = len(title.split())
    if nw > 25:
        out.append(Finding(WARN, "meta", "title-long",
                           "标题 %d 个词，偏长（多数期刊建议不超过 20 词）" % nw,
                           title[:80]))
    secs = _section_lines(m.text)
    if "abstract" in secs:
        later = [ln for sid, ln in secs.items() if ln > secs["abstract"]]
        end = min(later) if later else secs["abstract"] + 40
        seg = " ".join(lines[secs["abstract"] + 1:end])
        anw = len(seg.split())
        out.append(Finding(INFO, "meta", "abstract-words", "摘要约 %d 词" % anw))
        if anw > 400:
            out.append(Finding(WARN, "meta", "abstract-long",
                               "摘要 %d 词，超过多数期刊 250-350 词上限，请核对目标期刊要求" % anw))
    return out


ALL_CHECKS = [
    ("structure", check_structure),
    ("ethics", check_ethics),
    ("statistics", check_statistics),
    ("figures", check_figures),
    ("references", check_references),
    ("language", check_language),
    ("meta", check_meta),
]


def run_all(m):
    findings = []
    for _, fn in ALL_CHECKS:
        try:
            findings.extend(fn(m))
        except Exception as e:
            findings.append(Finding(WARN, "manulint", "check-error",
                                    "检查项执行异常（不影响其他项）：%s" % e))
    return findings


def score(findings):
    fails = sum(1 for f in findings if f.severity == FAIL)
    warns = sum(1 for f in findings if f.severity == WARN)
    s = max(0, 100 - 3 * fails - warns)
    if s >= 90:
        grade = "可投稿（建议再通读一遍）"
    elif s >= 70:
        grade = "小修后投稿"
    else:
        grade = "建议大修后再投"
    return s, grade
