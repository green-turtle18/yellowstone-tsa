# Isolated Person 1 branch work

All branch work now lives in `person1/`. Shared repository files were restored to the branch base (`d8bd978`). The folder includes unchanged copies of required original inputs, so analyses do not write into the shared project.

From the repository root, run:

```sh
.venv/bin/python person1/scripts/run_all.py
.venv/bin/python -m unittest discover -s person1/tests -v
.venv/bin/python person1/supplements/gap_research/build_supplement.py
```

Open notebooks with `person1/` or `person1/notebooks/` as the working directory. Instructions in the original README and reports use paths relative to `person1/`; use the repository's Python environment (for example `../.venv/bin/python` when inside this folder).

Data, results, provenance snapshots and existing handoff archives were preserved byte-for-byte during relocation. Archives retain their original internal relative layout. Read README.md for analysis details and supplements/gap_research/README.md for the data-gap findings.

The changes are not committed or pushed. Commit the relocation together (tracked root restorations/deletions plus the new person1 folder). Do not include local Python environments or caches. After committing, the net diff against the branch base should contain additions under person1 only. This reduces overlapping-file conflicts; it cannot guarantee that future independent edits never conflict.
