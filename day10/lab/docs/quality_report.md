# Quality Report - Lab Day 10

**run_id:** `clean-final`  
**Date:** 2026-06-10

## 1. Data Summary

| Metric | Inject / before | Clean / after | Notes |
|---|---:|---:|---|
| raw_records | 247 | 247 | same source CSV |
| cleaned_records | 34 | 34 | same row count; content differs because refund fix is disabled in inject |
| quarantine_records | 213 | 213 | invalid, stale, duplicate, and omitted rows are quarantined |
| Expectation halt? | yes, skipped intentionally | no | inject failed `refund_no_stale_14d_window` |

## 2. Before / After Retrieval

Artifacts:

- bad snapshot: `artifacts/eval/after_inject_bad.csv`
- clean snapshot: `artifacts/eval/after_fix_eval.csv`
- official grading: `artifacts/eval/grading_run.jsonl`

Key checks after the final clean run:

- `q_refund_window`: `contains_expected=yes`, `hits_forbidden=no`, `top1_doc_expected=yes`
- `q_hr_annual_leave_under3`: `contains_expected=yes`, `hits_forbidden=no`, `top1_doc_expected=yes`
- `q_access_level4`: `contains_expected=yes`, `hits_forbidden=no`, `top1_doc_expected=yes`

## 3. Freshness & Monitor

`manifest_clean-final.json` returns freshness `FAIL` because the latest export timestamp is `2026-04-10T00:00:00`, which is older than the 24 hour SLA on 2026-06-10. This is expected for the lab sample.

## 4. Corruption Inject

`inject-bad` disables the refund-window fix and uses `--skip-validate` to publish intentionally bad data. The expectation suite detects the corruption:

```text
expectation[refund_no_stale_14d_window] FAIL (halt) :: violations=1
```

The clean final run restores:

```text
expectation[refund_no_stale_14d_window] OK (halt) :: violations=0
```

## 5. Limitations

The environment lacked `chromadb`, so the run used local JSONL retrieval. The code still supports Chroma automatically when installed.
