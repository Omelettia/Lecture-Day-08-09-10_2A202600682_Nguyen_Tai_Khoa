# Individual Report - Lab Day 10: Data Pipeline & Observability

**Name:** Nguyen Tai Khoa  
**Role:** Ingestion, Cleaning, Quality, Embed, Monitoring  
**Submission date:** 2026-06-10  
**Final clean run_id:** `clean-final`  
**Inject run_id:** `inject-bad`

## 1. What I Was Responsible For

I handled the Day 10 pipeline end to end because this submission is an individual exercise. My main files were `transform/cleaning_rules.py`, `quality/expectations.py`, `etl_pipeline.py`, `grading_run.py`, `eval_retrieval.py`, and the documentation under `docs/` and `reports/`. I started from the raw CSV export and checked why the baseline pipeline could halt or miss grading-critical information. The final clean run produced `raw_records=247`, `cleaned_records=34`, and `quarantine_records=213`. I also generated the evidence artifacts in `artifacts/eval/`, `artifacts/logs/`, `artifacts/manifests/`, `artifacts/cleaned/`, and `artifacts/quarantine/`.

## 2. Technical Decision

The most important technical decision was to treat data correctness failures as halt-level checks when they could directly make the agent answer incorrectly. For example, `refund_no_stale_14d_window`, `hr_leave_no_stale_10d_annual`, `canonical_doc_coverage`, and `access_control_level4_approvers_present` are halt expectations. These checks protect facts that appear in the official grading questions. I kept `no_export_noise_prefixes` as warn because noisy prefixes hurt retrieval quality, but they are less dangerous than publishing a wrong policy value. I also kept the local JSONL fallback in the code, but the final verified run used Chroma collection `day10_kb` with `embed_upsert count=34`.

## 3. Anomaly Fixed

The first anomaly was that valid access-control rows existed in `policy_export_dirty.csv`, but the baseline allowlist did not include `access_control_sop`. That meant the pipeline could quarantine the very document needed for `gq_d10_10`. I fixed this by adding `access_control_sop` to `ALLOWED_DOC_IDS`, then adding `canonical_doc_coverage` and `access_control_level4_approvers_present` expectations. A second anomaly was stale HR 2025 text surviving with misleading 2026 dates. I fixed that by quarantining HR annual-leave text that still says `10 ngày phép năm (bản HR 2025)`, even when the effective date looks current. The clean run shows `hr_leave_no_stale_10d_annual OK :: violations=0`.

## 4. Before / After Evidence

For Sprint 3, I ran the intentional bad snapshot with:

```bash
python etl_pipeline.py run --run-id inject-bad --no-refund-fix --skip-validate
```

That run correctly logged:

```text
expectation[refund_no_stale_14d_window] FAIL (halt) :: violations=1
```

The retrieval evidence shows the effect clearly. In `artifacts/eval/after_inject_bad.csv`, `q_refund_window` retrieved the stale 14 day refund chunk and had `hits_forbidden=yes`. In `artifacts/eval/after_fix_eval.csv`, the same question retrieved the cleaned 7 working day chunk and had `hits_forbidden=no`. The final `grading_run.jsonl` passes all ten grading questions with `contains_expected=true`, `hits_forbidden=false`, and expected top-1 document matches.

## 5. Next Improvement

With two more hours, I would add a small unit test suite for `clean_rows()` and `run_expectations()`. The most useful tests would cover access-control allowlisting, HR stale text quarantine, refund 14-to-7 cleanup, duplicate-after-clean behavior, and the expected halt/warn severity for each new expectation.
