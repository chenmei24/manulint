# Contributing

Start with an issue describing the rule, expected behavior, actual behavior, installed version, and selected options. Use a short **synthetic** manuscript or generated image. Do not attach confidential manuscripts, credentials, or patient data.

## Local checks

```bash
python -m pip install .
python -m unittest discover -s tests -v
python -m manulint.demo --out-dir demo-output
```

For a parser or rule change, add a regression test with a meaningful expected result. Keep rules generic or configurable; journal-specific preferences should not become universal requirements. Describe extraction limits and avoid claims about publication readiness or ethical adequacy.

## Package checks

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*
```

Do not upload to PyPI or create release tags while developing. The release workflow uses trusted publishing and runs tests before uploading.
