# manulint

**Catch manuscript reporting and formatting issues before submission — locally, with no API key.**

[![Tests](https://github.com/chenmei24/manulint/actions/workflows/tests.yml/badge.svg)](https://github.com/chenmei24/manulint/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/manulint)](https://pypi.org/project/manulint/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/chenmei24/manulint/blob/master/LICENSE)

[简体中文](https://github.com/chenmei24/manulint/blob/master/README.zh-CN.md) · [Example report](https://github.com/chenmei24/manulint/blob/master/samples/synthetic_report.md) · [Report a bug](https://github.com/chenmei24/manulint/issues)

`manulint` reads Word (`.docx`), Markdown, and plain-text manuscripts. It flags expressions such as `p = 0.000`, repeated references, broken reference numbering, and low-resolution embedded figures. Select an original-research, review, or case-report profile instead of applying IMRaD to every article.

```text
manulint rule check | score 84/100 | 4 flagged rules / 4 warnings; score is unvalidated
[FLAG] Found 1 rounded p = 0.000 expressions; report p < 0.001 instead.
[FLAG] image1.png (occurrence 1): effective resolution 60 dpi (minimum axis).
[FLAG] Missing reference numbers (first 10): [3].
[FLAG] Repeated reference labels: [4].
[WARN] Found 1 potentially repeated reference entries after removing number labels.
```

This is an abbreviated excerpt from the [synthetic demonstration](https://github.com/chenmei24/manulint/blob/master/samples/synthetic_report.md). The example contains no patient data and supports no scientific claim. The score counts rule flags; it is **not a validated measure of publication readiness**.

## Try it in one command

Python 3.9 or later is required. From an installed package:

```bash
python -m manulint.demo --out-dir demo-output
```

This creates a fictional Markdown manuscript, a Word version with a deliberately low-resolution figure, and `demo-output/report.md`. It does not download data. Existing example files are preserved; choose a new output directory to run it again.

## Install

Install the latest published version:

```bash
python -m pip install --upgrade manulint
```

This README documents **0.1.1**. If the latest published version is older, install the repository version to use the profiles and new demonstration:

```bash
git clone https://github.com/chenmei24/manulint.git
cd manulint
python -m pip install .
```

## Check your manuscript

```bash
manulint paper.docx --md report.md
manulint paper.md --article-type review --language en --md review-report.md
manulint case.docx --article-type case-report --language zh
manulint paper.docx --p-style upper --md report.md
```

| Option | Default | Effect |
|---|---|---|
| `--article-type original\|review\|case-report` | `original` | Selects generic section and sample-size/test rules |
| `--language en\|zh\|auto` | `auto` | Controls punctuation rules and abstract counting; output is English |
| `--p-style lower\|upper\|either` | `either` | Warns about p/P case only when a particular style is selected |
| `--md OUT.md` | none | Writes an escaped Markdown report; never use the source path |
| `--cta https://...` | none | Adds an optional service URL to your report |
| `--version` | — | Prints the installed version |

**Exit codes:** `0` means checks completed, including when flags exist. `2` means invalid/empty/unreadable input, an invalid option, or a report-write failure. Exit `0` is not a scientific validation result. No report or score is generated for an empty manuscript.

## What is checked

| Category | Examples | Limits |
|---|---|---|
| Structure | Recognized headings, profile-specific required sections, disclosure headings | Generic profiles are not journal templates; absence of a heading is not proof that content is missing |
| Ethics | IRB/ethics-committee and informed-consent keywords; review profile skips these checks | Keywords cannot establish ethical adequacy or validate approval, consent, or exemptions |
| Statistics | Rounded `p = 0.000`, operator spacing, configured p/P case, sample-size/test/CI expressions | Does not recalculate results or assess test suitability; sample-size/test checks apply only to original research |
| Figures | Each body drawing resolved by relationship ID; effective DPI is the minimum of horizontal and vertical axes | 300 dpi is a screening threshold, not a universal journal requirement; vectors and unsupported images are explicitly skipped |
| References | Missing number labels, repeated labels, order, and matching text after removing labels | No DOI lookup, bibliographic verification, or citation-to-reference matching |
| Language | Chinese punctuation in English profiles, repeated spaces, mixed `Fig.`/`Figure` | Does not check grammar; automatic language detection can be wrong |
| Metadata | Abstract count excluding heading and structured labels; English title length | Counts English whitespace-delimited words or Chinese characters; journal counting conventions may differ |

## Important extraction limits

- Word extraction covers body paragraphs, table text, and modern embedded body drawings, in document order. Headers, footers, text boxes, footnotes, equations, charts, legacy VML pictures, and tracked-change text are not fully assessed.
- Reusing the same image at different displayed sizes creates separate resolution findings. DPI checks use displayed width **and** height, not image-file metadata. Cropping and journal-specific figure requirements still need manual review.
- Section detection expects recognizable English/Chinese headings. A structured abstract is separated using a later `Keywords` or `Introduction` heading; without those boundaries its end can be ambiguous. Unusual headings may be missed.
- Numbered references support `[1]`, `(1)`, `1.`, and `1)`. Wrapped continuation lines are joined; author-year duplicates are compared per non-empty line. References stop at recognized later sections or another Markdown heading.
- Files stay on the local computer. Remote Markdown images are not downloaded. Reports may contain excerpts and filenames from your manuscript, so review them before sharing.

## Scoring and interpretation

The score is `max(0, 100 - 3 × flagged rules - warnings)`. These weights are a convenience, **have not been validated**, and can count related issues more than once. Use the individual findings and the target journal's author instructions. A score of 100 does not establish completeness, scientific quality, ethical adequacy, or acceptance likelihood.

## Contribute

Please report a reproducible rule failure with a small **synthetic** example. Do not upload confidential manuscripts or patient data. See [CONTRIBUTING.md](https://github.com/chenmei24/manulint/blob/master/CONTRIBUTING.md) for local checks and [CHANGELOG.md](https://github.com/chenmei24/manulint/blob/master/CHANGELOG.md) for changes.

```bash
python -m pip install .
python -m unittest discover -s tests -v
python -m manulint.demo --out-dir demo-output
```

CI is configured for Linux and Windows on Python 3.9, 3.11, and 3.13. Tagged PyPI publication runs the regression suite and distribution checks before trusted publishing.

## License

[MIT](https://github.com/chenmei24/manulint/blob/master/LICENSE).

## Related tools / 相关工具

- [Medical-imaging manifest audits](https://github.com/chenmei24/dicleak)
- [Traceable clinical CSV QA](https://github.com/chenmei24/clinical-imaging-data-qa-demo)

[Launch tutorials and share images / 推广教程与展示图](docs/launch/README.md)
