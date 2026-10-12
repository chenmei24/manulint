# manulint launch kit / 发布材料

Publication drafts for the next checked release. No community post has been sent by this kit. Verify commands and implemented rules before copying.

## Positioning / 一句话定位

**EN:** A local, rule-based checklist for manuscript structure, reporting, references, and embedded figures.

**中文：** 在本地用规则检查论文结构、报告规范、参考文献和内嵌图片，生成投稿前自查清单。

Primary audience: researchers preparing an academic manuscript. Findings are reminders for human review. The score is a summary of configured checks, not a submission recommendation, scientific quality rating, or prediction of journal acceptance.

## Reproducible tutorial / 可复现教程

### Turn pre-submission reminders into a reviewable checklist

From a clone of this repository:

```bash
python -m pip install -e .
manulint samples/sample_manuscript.md --md sample-review.md
```

Use the committed sample before trying a real manuscript. Open the Markdown report and compare each finding with the actual text and the journal's author instructions. The sample is an illustration, not a research result. A zero exit code for a completed run is not evidence that a manuscript is ready to submit.

For your own authorized local document:

```bash
manulint paper.docx --md paper-review.md
```

Choose a generic article profile and language when relevant, for example:

```bash
manulint paper.docx --article-type case-report --language en --p-style either --md paper-review.md
```

The available article profiles are `original`, `review`, and `case-report`; they are generic rule configurations, not templates certified against a particular journal. The `--p-style` option controls capitalization reminders (`lower`, `upper`, or `either`).

Supported inputs include `.docx`, `.md`, and `.txt`. Modern Word body drawing resolution checks depend on the embedded image's pixels and its displayed size. An unreadable or unmeasurable image needs manual review; a default DPI threshold is not a universal journal standard. External figure files and other report requirements also need review against the target journal.

A useful review sequence:

1. Correct input/extraction errors before interpreting findings.
2. Open the exact paragraph, reference, or figure named in each finding.
3. Confirm whether the rule applies to the study type and target journal.
4. Correct only verified issues; never invent an ethics approval, consent waiver, sample size, confidence interval, or citation to silence a warning.
5. Rerun the checklist and retain the report alongside the manuscript version.

**中文解读：** 先用仓库内示例生成报告，再对自己的 Word/Markdown/文本稿件检查。可以选择原始研究、综述或病例报告的通用配置，并指定语言和 p/P 风格；这些配置不是已认证的目标期刊模板。逐条定位、核对目标期刊要求、确认后修改；工具的评分只概括规则结果。图片分辨率需要结合显示尺寸和目标期刊要求判断。规则没有提示某项，并不代表内容完整；检测到伦理关键词，也不代表伦理审批真实有效。

### Example of an appropriate correction / 合理修改示例

If statistical software displays `p = 0.000` because of rounding, confirm the underlying value before changing the manuscript to an appropriate bound such as `p < 0.001`. Do not fabricate an exact value. The tool can flag the string; it cannot verify the underlying analysis.

For suspected duplicate references, compare the source entries and citations before removing or renumbering anything. Similar text may refer to distinct publications; a rule is a prompt to inspect.

## Copy-ready launch posts / 可复制发布文案

### Chinese tutorial post

**标题：投稿前自查：把规范问题变成一份可复核的清单**

论文准备投稿时，章节、伦理声明、统计表述、参考文献和图片尺寸需要反复核对。我做了 manulint，一个在本地运行的规则检查工具，支持 Word、Markdown 和文本文件，并输出 Markdown 自查报告。

可以先用仓库的示例试跑，再逐条对照目标期刊《作者指南》。它帮助定位需要人工核对的地方，不评判研究质量，不替代同行评议，也不能保证投稿录用。伦理和统计提醒必须根据真实审批和原始分析处理，不能为了消除提示补造内容。

欢迎用合成文本反馈误报、漏报和不同稿件结构的兼容问题。

代码与运行示例：https://github.com/chenmei24/manulint

### English technical post

**Title: A local checklist for manuscript preparation, with inspectable findings**

I built **manulint**, a local rule-based CLI for pre-submission manuscript checks. It accepts Word, Markdown, and text files, checks selected structure/reporting/reference/figure rules, and can export a Markdown review checklist.

The purpose is to help authors locate items for manual verification against their target journal. A score summarizes rules; it does not assess scientific merit, verify ethics approval, or predict acceptance. Statistical warnings must be resolved from the actual analysis, never by inventing values.

A sample manuscript and runnable command are included. Feedback on false positives and manuscript structures is welcome through minimal synthetic examples.

Repository: https://github.com/chenmei24/manulint

### Short release announcement

**中文：** manulint 更新：完善空文档处理、摘要计数、重复参考文献及 Word 图片匹配。输出用于人工复核的规则清单；不保证录用。先运行仓库示例，再核对目标期刊要求。

**EN:** manulint update: improved empty-input handling, abstract counting, duplicate-reference checks, and Word image matching. Local rules for human review, not acceptance prediction. Try the committed sample first.

Verify each stated change against the checked release before posting; this draft does not claim an uploaded package version.

## Assets / 展示图

- [Vector social card](../../assets/launch/social-preview.svg), 1280 × 640.
- [PNG social card](../../assets/launch/social-preview.png), rendered from the SVG.
- The checklist card is a conceptual illustration, not an output screenshot or a testimonial.

## 30-day execution calendar / 30天执行日历

Day 1 begins when the corrected release is public. Keep this project's launch secondary to dicleak, and stagger posts so each has a concrete use case. Posting is not performed by this kit.

| Days | Action / 行动 | Evidence to record / 留存证据 |
| --- | --- | --- |
| 1–3 | Verify clean installation, sample report, empty-input failure, and current release notes | Commands and actual outputs |
| 4–6 | Set description/topics/social image; link the sample and plain scope statement | Repository page, preview image |
| 7–10 | Publish one Chinese tutorial showing how to verify a finding manually | Post URL and substantive feedback |
| 11–14 | Invite one relevant researcher to try the sample; collect voluntary structured feedback | Release, command, reproduced issue |
| 15–17 | Publish the English walkthrough in one venue that permits relevant tool posts | Post URL, questions and traffic snapshot |
| 18–21 | Document one real compatibility issue with a synthetic input; add a fix or explain a limit | Issue, regression test or limitation note |
| 22–24 | Add one guide to interpreting statistical/ethics reminders without inventing content | Reviewed guide URL |
| 25–27 | Demonstrate Word image-size versus pixel-size handling with a generated figure | Synthetic input and actual finding |
| 28–30 | Review usable feedback and traffic; choose a narrow next rule or journal configuration | Evidence-backed next-release scope |

## Measurement / 衡量方式

| Metric | Method | Interpretation |
| --- | --- | --- |
| Visitors / unique visitors | Save weekly, dated GitHub Traffic snapshots | Readers reached; not confirmed users |
| Clones / unique cloners | Use the same period as visitor counts | Source exploration; not successful installs |
| Voluntary successful runs | Record sample command and release from tester feedback | Whether onboarding works |
| Reproducible issues | Count unique reports with synthetic text or documents | Which rule/extraction work matters |
| False positives resolved | Record a test or an explicitly documented limit | Rule quality rather than more rules |
| Qualified inquiries | Count requests for a concrete scoped workflow separately from free support | Related service demand |

Rolling traffic windows overlap. Do not sum their unique-visitor counts as 30-day unique users, or interpret a clone as an active user. Use an initial baseline and weekly snapshots. No star, visitor, or income outcomes are promised.

Tracking fields: date, release, channel/post URL, traffic window, visitors, unique visitors, clones, unique cloners, sample-run feedback, reproducible issues, resolutions, qualified inquiries, next action. Do not collect confidential manuscripts in public issues.

## Publication check / 发布前核对

- [ ] Current sample run and error handling match the description.
- [ ] Scoring is described as a rule summary; no acceptance claim appears.
- [ ] No unimplemented CONSORT/STROBE/PRISMA coverage, DOI validation, or journal profile is claimed.
- [ ] Word figure support is described with its actual measured scope and limitations.
- [ ] The venue permits the post; requests for feedback use synthetic reproductions.
