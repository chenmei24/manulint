"""Local heuristic checks, not scientific, ethical, or publication validation."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .readers import Manuscript

FAIL, WARN, INFO = "fail", "warn", "info"


@dataclass(frozen=True)
class CheckConfig:
    article_type: str = "original"
    language: str = "auto"
    p_style: str = "either"

    def __post_init__(self):
        for name, choices in (("article_type", ("original", "review", "case-report")),
                              ("language", ("en", "zh", "auto")),
                              ("p_style", ("lower", "upper", "either"))):
            if getattr(self, name) not in choices:
                raise ValueError(f"Invalid {name}: {getattr(self, name)}")


@dataclass
class Finding:
    severity: str
    check: str
    rule: str
    message: str
    evidence: str = ""


SECTION_PATTERNS = {
    "abstract": r"abstract|摘要",
    "keywords": r"key\s?words|关键词",
    "introduction": r"introduction|引言|前言",
    "methods": r"methods?|materials?\s+and\s+methods?|方法|材料与方法|资料与方法",
    "results": r"results?|结果",
    "discussion": r"discussion|讨论",
    "conclusion": r"conclusions?|结论",
    "references": r"references?|参考文献",
    "acknowledgments": r"acknowledg(?:e)?ments?|致谢",
    "ethics": r"ethics?(?:\s+(?:approval|statement|declaration))?|ethical\s+approval|伦理(?:声明|审批)?",
    "conflict": r"conflicts?\s+of\s+interest|competing\s+interests|利益冲突",
    "funding": r"funding(?:\s+(?:statement|sources))?|基金|资助",
    "data_availability": r"data\s+availability(?:\s+statement)?|数据可用性",
    "case_presentation": r"case\s+(?:presentation|report)|病例(?:介绍|报告|资料)",
    "appendix": r"appendi(?:x|ces)(?:\s+[A-Z0-9]+)?|附录",
    "supplementary": r"supplement(?:ary|al)(?:\s+(?:materials?|data|information))?|补充材料",
}
REQUIRED_SECTIONS = {
    "original": ("abstract", "introduction", "methods", "results", "discussion", "references"),
    "review": ("abstract", "introduction", "references"),
    "case-report": ("abstract", "introduction", "case_presentation", "discussion", "references"),
}
RECOMMENDED_SECTIONS = ("keywords", "conflict", "funding", "data_availability")
INLINE_SECTIONS = {"abstract", "keywords", "ethics", "conflict", "funding", "data_availability"}


def _heading(raw):
    line = re.sub(r"^\s*#{1,6}\s+", "", raw).strip()
    line = re.sub(r"^\d+(?:\.\d+)*[.)]?\s+", "", line)
    line = line.strip("*_ ").strip()
    for sid, pattern in SECTION_PATTERNS.items():
        if re.fullmatch(rf"(?:{pattern})\s*[:：]?", line, re.I):
            return sid, ""
        if sid in INLINE_SECTIONS:
            match = re.fullmatch(rf"(?:{pattern})\s*[:：]\s*(.+)", line, re.I)
            if match:
                return sid, match.group(1)
    return None, ""


def _section_lines(text):
    candidates = [(i, _heading(raw)[0]) for i, raw in enumerate(text.splitlines())]
    abstract = next((i for i, sid in candidates if sid == "abstract"), None)
    # Structured-abstract Methods/Results/Conclusions are not body sections.
    boundary = next((i for i, sid in candidates if abstract is not None and i > abstract
                     and sid in ("keywords", "introduction")), None)
    found = {}
    for i, sid in candidates:
        if sid is None or sid in found:
            continue
        if abstract is not None and boundary is not None and abstract < i < boundary:
            continue
        found[sid] = i
    return found


def _language(m, config):
    if config.language != "auto":
        return config.language
    chinese = len(re.findall(r"[\u4e00-\u9fff]", m.text))
    latin = len(re.findall(r"[A-Za-z]", m.text))
    return "zh" if chinese > latin / 2 else "en"


def check_structure(m, config=CheckConfig()):
    sections = _section_lines(m.text)
    out = [Finding(FAIL, "structure", "missing-" + sid,
                   f"No [{sid}] heading detected for the {config.article_type} profile; verify the journal's required structure.")
           for sid in REQUIRED_SECTIONS[config.article_type] if sid not in sections]
    out.extend(Finding(WARN, "structure", "missing-" + sid,
                       f"No [{sid}] heading detected; verify whether a separate statement is required.")
               for sid in RECOMMENDED_SECTIONS if sid not in sections)
    return out or [Finding(INFO, "structure", "ok", "Configured section headings were detected; content was not validated.")]


def check_ethics(m, config=CheckConfig()):
    if config.article_type == "review":
        return [Finding(INFO, "ethics", "profile-skip",
                        "Ethics keyword checks skipped for the review profile; authors must determine whether approval or consent applies.")]
    out = []
    has_irb = bool(re.search(r"ethics?\s*committee|institutional review board|\bIRB\b|伦理委员会", m.text, re.I))
    has_consent = bool(re.search(r"informed consent|知情同意", m.text, re.I))
    if config.article_type == "original" and not has_irb:
        out.append(Finding(WARN, "ethics", "no-irb", "No ethics committee/IRB keywords found; verify whether approval or an exemption statement is needed."))
    if not has_consent:
        out.append(Finding(WARN, "ethics", "no-consent", "No informed-consent keywords found; verify applicable consent or waiver requirements."))
    out.append(Finding(INFO, "ethics", "not-validated",
                       "Keyword presence cannot establish ethical adequacy, approval validity, consent, or legal compliance."))
    return out


P_ZERO = re.compile(r"\b[pP]\s*=\s*0\.000\b")
P_VALUE = re.compile(r"\b[pP]\s*[=<>]")
N_REPORTED = re.compile(r"\bn\s*=\s*\d+|样本量|纳入\s*\d+\s*例", re.I)
TEST_NAMED = re.compile(r"t[-\s]?test|chi[-\s]?square|ANOVA|ANCOVA|Mann[-\s]?Whitney|Wilcoxon|Kruskal[-\s]?Wallis|regression|logistic|\bCox\b|Kaplan[-\s]?Meier|Fisher|t检验|卡方|回归", re.I)
CI_REPORTED = re.compile(r"95\s?%\s?CI|confidence interval|置信区间", re.I)


def check_statistics(m, config=CheckConfig()):
    out = []
    zeros = P_ZERO.findall(m.text)
    if zeros:
        out.append(Finding(FAIL, "statistics", "p-zero", f"Found {len(zeros)} rounded p = 0.000 expressions; report p < 0.001 instead.", "; ".join(zeros[:3])))
    if config.p_style != "either":
        unexpected = "P" if config.p_style == "lower" else "p"
        if re.search(rf"\b{unexpected}\s*[=<>]", m.text):
            out.append(Finding(WARN, "statistics", "p-case", f"P-value case differs from the selected '{config.p_style}' style; check the target journal."))
    if re.search(r"\b[pP][=<>]\s*\d|\b[pP]\s*[=<>]\d", m.text):
        out.append(Finding(WARN, "statistics", "p-nospace", "P-value operators lack surrounding spaces (example: p = 0.03); confirm the journal's style."))
    if config.article_type == "original":
        if not N_REPORTED.search(m.text):
            out.append(Finding(WARN, "statistics", "no-n", "No sample-size expression was recognized; verify sample sizes are reported."))
        if not TEST_NAMED.search(m.text):
            out.append(Finding(WARN, "statistics", "no-test", "No named statistical test was recognized; this heuristic does not assess whether a test is needed or appropriate."))
    if P_VALUE.search(m.text) and not CI_REPORTED.search(m.text):
        out.append(Finding(WARN, "statistics", "no-ci", "P-values detected but no confidence-interval expression recognized; check the relevant reporting requirements."))
    if not out and config.article_type == "case-report":
        return [Finding(INFO, "statistics", "profile-skip", "No statistical expressions flagged; sample-size and named-test checks are skipped for the case-report profile.")]
    return out or [Finding(INFO, "statistics", "ok", "No configured statistical-expression rules flagged; analysis was not validated.")]


def check_figures(m, config=CheckConfig()):
    out = [Finding(INFO, "figures", "skipped", note) for note in m.notes]
    if not m.figures:
        return out + [Finding(INFO, "figures", "none-found", "No supported body image occurrences detected; external figures were not assessed.")]
    for figure in m.figures:
        if figure.skip_reason or figure.image is None:
            out.append(Finding(INFO, "figures", "skipped", f"{figure.name}: {figure.skip_reason or 'Image unavailable.'}"))
            continue
        width, height = figure.image.size
        if not figure.width_in or not figure.height_in or figure.width_in <= 0 or figure.height_in <= 0:
            out.append(Finding(INFO, "figures", "unknown-size", f"{figure.name}: {width} x {height} pixels; displayed width/height unknown, so effective DPI was not assessed."))
            continue
        dpi_x, dpi_y = width / figure.width_in, height / figure.height_in
        dpi = min(dpi_x, dpi_y)
        severity = FAIL if dpi < 150 else WARN if dpi < 300 else INFO
        rule = "low-dpi" if dpi < 300 else "dpi-ok"
        out.append(Finding(severity, "figures", rule,
                           f"{figure.name}: effective resolution {dpi:.0f} dpi (minimum axis); 300 dpi is a screening threshold, not a universal journal requirement.",
                           f"{width} x {height} px; display {figure.width_in:.2f} x {figure.height_in:.2f} in; x/y {dpi_x:.0f}/{dpi_y:.0f} dpi"))
    return out


REF_NUMBER = re.compile(r"^\s*(?:\[(\d+)\]|\((\d+)\)|(\d+)[.)])\s*(\S.*)$")


def check_references(m, config=CheckConfig()):
    sections = _section_lines(m.text)
    if "references" not in sections:
        return []
    lines = m.text.splitlines()
    start = sections["references"] + 1
    end = next((i for i in range(start, len(lines)) if _heading(lines[i])[0]
                or re.match(r"^\s*#{1,6}\s+", lines[i])), len(lines))
    entries, numbers = [], []
    for raw in lines[start:end]:
        line = raw.strip()
        if not line:
            continue
        match = REF_NUMBER.match(line)
        if match:
            numbers.append(int(next(value for value in match.groups()[:3] if value is not None)))
            entries.append(match.group(4))
        elif numbers and entries:
            entries[-1] += " " + line
        else:
            entries.append(line)
    out = []
    if not numbers:
        out.append(Finding(INFO, "references", "unparsed", "No numbered reference format recognized; numbering checks skipped (author-year entries may be used)."))
    else:
        missing = []
        expected = 1
        for number in sorted(set(numbers)):
            if number > expected:
                missing.extend(range(expected, min(number, expected + 10 - len(missing))))
            expected = number + 1
        if missing:
            out.append(Finding(FAIL, "references", "number-gap", f"Missing reference numbers (first 10): {missing}."))
        duplicates = sorted(number for number, count in Counter(numbers).items() if count > 1)
        if duplicates:
            out.append(Finding(FAIL, "references", "number-duplicate", f"Repeated reference labels: {duplicates[:10]}."))
        if numbers != sorted(numbers):
            out.append(Finding(WARN, "references", "number-order", "Reference labels appear out of ascending order."))
        if not out:
            out.append(Finding(INFO, "references", "ok", f"Reference labels are consecutive, unique, and ordered ({len(numbers)} entries)."))
    normalized = [re.sub(r"\s+", " ", entry.casefold()).strip() for entry in entries]
    repeated = sum(count - 1 for count in Counter(normalized).values() if count > 1)
    if repeated:
        out.append(Finding(WARN, "references", "duplicates", f"Found {repeated} potentially repeated reference entries after removing number labels."))
    return out


def check_language(m, config=CheckConfig()):
    out = []
    punctuation = re.findall(r"[，。；：、（）《》]", m.text)
    if _language(m, config) == "en" and punctuation:
        out.append(Finding(WARN, "language", "cjk-punct", f"Found {len(punctuation)} Chinese punctuation characters in an English-language profile."))
    doubles = len(re.findall(r" {2,}", m.text))
    if doubles > 10:
        out.append(Finding(WARN, "language", "double-space", f"Found {doubles} repeated-space runs; check intentional alignment before replacing."))
    short, long = len(re.findall(r"\bFig\.", m.text)), len(re.findall(r"\bFigure\b", m.text))
    if short and long:
        out.append(Finding(WARN, "language", "fig-mixed", f"Fig. ({short}) and Figure ({long}) are mixed; check the required caption style."))
    return out or [Finding(INFO, "language", "ok", "No configured punctuation/style rules flagged.")]


def check_meta(m, config=CheckConfig()):
    if not m.text.strip():
        raise ValueError("Manuscript has no extractable text.")
    lines = m.text.splitlines()  # Same unfiltered indexes as _section_lines.
    title = next(line.strip() for line in lines if line.strip())
    out = []
    if _language(m, config) == "en" and len(title.lstrip("# ").split()) > 25:
        out.append(Finding(WARN, "meta", "title-long", "Title exceeds 25 words; verify the target journal's limit.", title[:100]))
    sections = _section_lines(m.text)
    if "abstract" in sections:
        start = sections["abstract"]
        later = [index for index in sections.values() if index > start]
        end = min(later) if later else len(lines)
        content = []
        for line in [_heading(lines[start])[1]] + lines[start + 1:end]:
            stripped = re.sub(r"^\s*#{1,6}\s+", "", line).strip().strip("*_ ")
            label = re.match(r"^(?:background|objectives?|purpose|methods?|results?|conclusions?|背景|目的|方法|结果|结论)(?:\s*[:：]\s*|\s*$)", stripped, re.I)
            content.append(stripped[label.end():] if label else stripped)
        abstract = " ".join(content)
        if _language(m, config) == "zh":
            count = len(re.findall(r"[\u4e00-\u9fff]", abstract))
            out.append(Finding(INFO, "meta", "abstract-characters", f"Abstract contains approximately {count} Chinese characters; structured labels are excluded (Latin words are not counted)."))
        else:
            count = len(abstract.split())
            out.append(Finding(INFO, "meta", "abstract-words", f"Abstract contains approximately {count} whitespace-delimited words; heading and structured labels are excluded."))
            if count > 400:
                out.append(Finding(WARN, "meta", "abstract-long", f"Abstract exceeds 400 words ({count}); verify the target journal's exact limit."))
    return out


ALL_CHECKS = (check_structure, check_ethics, check_statistics, check_figures,
              check_references, check_language, check_meta)


def run_all(m, config=CheckConfig()):
    if not m.text.strip():
        raise ValueError("Manuscript has no extractable text.")
    findings = []
    for check in ALL_CHECKS:
        findings.extend(check(m, config))
    return findings


def score(findings):
    """Preserve the simple point count, explicitly without readiness claims."""
    fails = sum(f.severity == FAIL for f in findings)
    warnings = sum(f.severity == WARN for f in findings)
    value = max(0, 100 - 3 * fails - warnings)
    label = f"{fails} flagged rules / {warnings} warnings; score is unvalidated"
    return value, label
