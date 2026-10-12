# Changelog

## 0.1.1 — 2026-10-12

- Reject empty or unreadable manuscripts with input-error exit code 2; prevent report/source path collisions.
- Replace publication recommendations with explicitly unvalidated rule counts and scoring.
- Fix blank-line abstract indexes, structured-abstract counting, and body-heading false matches.
- Detect duplicate reference content after removing labels; separate missing labels, repeated labels, and out-of-order labels; stop at later sections.
- Resolve Word figures by relationship ID for every occurrence; use both displayed width and height, including reused images; explicitly skip vectors and unsupported images.
- Preserve body paragraph/table order and explain malformed DOCX errors.
- Add original/review/case-report profiles, manuscript-language selection, and configurable p/P style.
- Clarify that ethics keywords cannot establish ethical adequacy; escape manuscript fields in Markdown reports.
- Add a synthetic one-command demonstration, English/Chinese documentation, package URLs, contribution templates, and regression CI.

## 0.1.0 — 2026-10-11

- Initial local manuscript checklist and PyPI trusted-publishing workflow.
