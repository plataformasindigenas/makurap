# One-time seed scripts (retired from the build)

`prepare_dictionary.py` and `prepare_fauna_flora.py` generated `data/dictionary.tsv`,
`data/fauna.yaml` and `data/ethnobotany.yaml` from `raw/*.xlsx`. They were run once on
2026-10-09 to seed the tracked files in `data/`; their output was verified byte-identical
to what was live. **They are no longer part of the build** and must not be re-run against
`data/`: that would overwrite edits. `data/*.tsv|yaml` are now the source of truth (and
will be fed from a Google Sheet).
