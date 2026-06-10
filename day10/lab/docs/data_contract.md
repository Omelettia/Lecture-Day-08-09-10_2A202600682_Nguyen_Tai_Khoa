# Data Contract - Lab Day 10

This document mirrors `contracts/data_contract.yaml` and records the operational source map for the cleaned knowledge-base export.

## 1. Source Map

| Source | Ingest method | Main failure mode | Metric / alert |
|---|---|---|---|
| `policy_refund_v4` | CSV export from CS policy system | stale 14 day refund chunk, duplicated sync rows | `refund_no_stale_14d_window`, `hits_forbidden` |
| `sla_p1_2026` | CSV export from incident/SLA docs | invalid doc IDs, duplicate P1 chunks | canonical doc coverage, top1 doc check |
| `it_helpdesk_faq` | CSV export from helpdesk FAQ | missing text, duplicated lockout/VPN rows | cleaned/quarantine count, keyword eval |
| `hr_leave_policy` | CSV export from HR policy source | 2025 annual leave text mixed with 2026 dates | `hr_leave_no_stale_10d_annual` |
| `access_control_sop` | CSV export from access workflow docs | valid source omitted from baseline allowlist | `access_control_level4_approvers_present` |

## 2. Cleaned Schema

| Column | Type | Required | Notes |
|---|---|---|---|
| `chunk_id` | string | yes | stable ID from `doc_id`, final cleaned text, and sequence |
| `doc_id` | string | yes | must be in the allowlist |
| `chunk_text` | string | yes | normalized source text, min length 8 |
| `effective_date` | date | yes | normalized to `YYYY-MM-DD` |
| `exported_at` | datetime | yes | source export timestamp used for freshness |

## 3. Quarantine vs Drop

Rows are written to `artifacts/quarantine/quarantine_<run_id>.csv` with a `reason`. They are not silently dropped. Re-entry requires changing either source data or a named cleaning rule, followed by rerunning expectations and retrieval eval.

## 4. Canonical Versions

- Refund current version: `policy_refund_v4`, refund window must be 7 working days.
- HR current version: `hr_leave_policy` with effective date from `2026-01-01`; 2025 annual leave text is stale even if a row has a 2026 effective date.
- Access control current source: `access_control_sop`, required for Level 4 Admin Access questions.
