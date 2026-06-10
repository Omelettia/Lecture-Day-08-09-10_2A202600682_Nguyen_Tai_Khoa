# Group Report - Lab Day 10: Data Pipeline & Data Observability

**Group:** 2A202600682 - Nguyen Tai Khoa  
**Submission date:** 2026-06-10  
**Final clean run_id:** `clean-final`  
**Inject run_id:** `inject-bad`

## 1. Pipeline Overview

The raw input is `data/raw/policy_export_dirty.csv`, a simulated multi-source export for the CS and IT Helpdesk knowledge base. The pipeline loads raw rows, normalizes and quarantines invalid rows, validates cleaned rows with halt/warn expectations, then publishes the retrieval index. In this environment `chromadb` was not installed, so the pipeline used the built-in local JSONL fallback at `artifacts/index/local_index.jsonl`; the Chroma path remains available when dependencies are installed.

One command for the final run:

```bash
python etl_pipeline.py run --run-id clean-final
```

Final counts: `raw_records=247`, `cleaned_records=34`, `quarantine_records=213`.

## 2. Cleaning & Expectations

New cleaning coverage includes `access_control_sop` in the allowlist, export-noise cleanup, repeated `lam viec` collapse, HR 2025 annual-leave text quarantine even when the date is misleading, and dedupe after final cleaning/fixes.

### 2a. metric_impact

| Rule / Expectation | Before | After / inject | Evidence |
|---|---:|---:|---|
| `stale_hr_policy_text_2025` | baseline halt: `hr_leave_no_stale_10d_annual` had 2 violations | clean-final: 0 violations | `artifacts/logs/run_clean-final.log` |
| `access_control_sop` allowlist | baseline quarantined all access-control rows as unknown | clean-final includes `access_control_level4_approvers_present matching_chunks=1` | `artifacts/cleaned/cleaned_clean-final.csv` |
| dedupe after refund fix | stale 14-day row could survive as distinct text before final dedupe | inject shows `refund_no_stale_14d_window FAIL violations=1`; clean-final has 0 | `artifacts/logs/run_inject-bad.log`, `run_clean-final.log` |
| `canonical_doc_coverage` | would fail when access-control was omitted | clean-final `missing_doc_ids=[]` | `artifacts/logs/run_clean-final.log` |
| `no_export_noise_prefixes` | noisy prefixes existed in raw rows | clean-final `noisy_chunks=0` | `artifacts/logs/run_clean-final.log` |

## 3. Before / After Retrieval

Intentional corruption used:

```bash
python etl_pipeline.py run --run-id inject-bad --no-refund-fix --skip-validate
python eval_retrieval.py --out artifacts/eval/after_inject_bad.csv
```

The inject run correctly failed `refund_no_stale_14d_window` with `violations=1` and continued only because `--skip-validate` was intentional for Sprint 3. The final clean eval is `artifacts/eval/after_fix_eval.csv`; the official grading output is `artifacts/eval/grading_run.jsonl`.

Final grading result: all `gq_d10_01` through `gq_d10_10` have `contains_expected=true`, `hits_forbidden=false`, and expected top-1 document matches where required.

## 4. Freshness & Monitoring

`manifest_clean-final.json` reports `latest_exported_at=2026-04-10T00:00:00`. On the lab date 2026-06-10, the default 24 hour SLA returns freshness `FAIL`. This is expected for the static sample data and should be treated as a monitor signal, not a failed pipeline run.

## 5. Day 09 Link

Day 10 prepares the corpus that Day 09 retrieval and synthesis workers should consume. The supervisor/worker stack should read only from the cleaned, validated index, which prevents the Day 09 agent from routing to stale HR/refund context.

## 6. Remaining Risks

- The local fallback is deterministic and passes the lab checks, but production should install Chroma or another vector store.
- Freshness needs a real source watermark in production instead of relying only on exported CSV timestamps.
