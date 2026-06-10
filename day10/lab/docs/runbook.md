# Runbook - Lab Day 10

## Symptom

The agent or retrieval eval returns stale or missing policy information, for example:

- refund window says 14 working days instead of 7
- HR annual leave says 10 days for under 3 years instead of 12
- Level 4 Admin Access cannot retrieve IT Manager and CISO approval

## Detection

Use these checks in order:

1. `python etl_pipeline.py run`
2. `python eval_retrieval.py --out artifacts/eval/after_fix_eval.csv`
3. `python grading_run.py --out artifacts/eval/grading_run.jsonl`
4. `python instructor_quick_check.py --grading artifacts/eval/grading_run.jsonl --manifest artifacts/manifests/manifest_clean-final.json`

Key signals:

- halt expectation failure, especially `refund_no_stale_14d_window` or `hr_leave_no_stale_10d_annual`
- `hits_forbidden=true` in eval/grading
- `top1_doc_matches=false` for grading IDs with expected source docs
- freshness `FAIL` when `latest_exported_at` is older than the SLA

## Diagnosis

| Step | Action | Expected result |
|---|---|---|
| 1 | Open `artifacts/logs/run_<run_id>.log` | counts show raw, cleaned, quarantine, and expectation details |
| 2 | Open `artifacts/quarantine/quarantine_<run_id>.csv` | invalid or stale rows include a clear `reason` |
| 3 | Compare `after_inject_bad.csv` and `after_fix_eval.csv` | bad run exposes stale refund context; clean run removes it |
| 4 | Inspect `artifacts/manifests/manifest_<run_id>.json` | run ID, counts, index backend, and freshness timestamp are present |

## Mitigation

- If an expectation halt is legitimate, do not publish the index; fix cleaning rules or source data and rerun.
- If `--skip-validate` was used for Sprint 3 injection, immediately rerun a clean pipeline afterward.
- If the index contains stale chunks, rerun `python etl_pipeline.py run --run-id clean-final`; Chroma mode prunes old IDs and local fallback rewrites the snapshot.

## Prevention

- Keep `ALLOWED_DOC_IDS` synchronized with `contracts/data_contract.yaml`.
- Add halt expectations for grading-critical facts and warn expectations for quality smells.
- Alert on freshness at the publish boundary. The sample data fails a 24 hour SLA on 2026-06-10 because the latest export is `2026-04-10T00:00:00`; this is expected for the lab snapshot and should be documented rather than ignored.
