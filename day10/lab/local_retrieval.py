from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parent
LOCAL_INDEX = ROOT / "artifacts" / "index" / "local_index.jsonl"

_TOKEN = re.compile(r"\w+", re.UNICODE)
_STOPWORDS = {
    "theo",
    "cho",
    "cua",
    "cua",
    "la",
    "va",
    "voi",
    "sau",
    "bao",
    "lau",
    "nhieu",
    "duoc",
    "trong",
    "chinh",
    "sach",
    "hien",
    "hanh",
    "can",
    "yeu",
    "cau",
}


def _tokens(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN.findall(text or "") if len(t) > 1]


def _norm_tokens(text: str) -> List[str]:
    return [t for t in _tokens(text) if t not in _STOPWORDS]


def write_local_index(rows: List[Dict[str, Any]], path: Path = LOCAL_INDEX) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_local_index(path: Path = LOCAL_INDEX) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def query_local_index(
    question: str,
    *,
    n_results: int,
    rows: List[Dict[str, Any]] | None = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    rows = rows if rows is not None else load_local_index()
    q_tokens = _norm_tokens(question)
    q_set = set(q_tokens)
    q_lower = question.lower()

    ranked: List[Tuple[float, int, Dict[str, Any]]] = []
    for i, row in enumerate(rows):
        doc = str(row.get("chunk_text") or "")
        doc_lower = doc.lower()
        d_tokens = _norm_tokens(doc)
        d_set = set(d_tokens)
        overlap = q_set & d_set
        score = float(len(overlap) * 4)
        score += sum(1 for t in q_tokens if t in d_set) * 0.25

        for phrase in (
            "level 4",
            "admin access",
            "it manager",
            "ciso",
            "finance team",
            "vpn",
            "p1",
            "15",
            "4",
            "10",
            "12",
            "2",
            "5",
        ):
            if phrase in q_lower and phrase in doc_lower:
                score += 6

        if row.get("doc_id") in q_lower:
            score += 3

        ranked.append((score, -i, row))

    ranked.sort(reverse=True)
    top = [r for score, _pos, r in ranked[:n_results] if score > 0]
    if len(top) < n_results:
        used_ids = {id(r) for r in top}
        top.extend(r for _score, _pos, r in ranked if id(r) not in used_ids)  # pragma: no cover
        top = top[:n_results]

    docs = [str(r.get("chunk_text") or "") for r in top]
    metas = [
        {
            "doc_id": str(r.get("doc_id") or ""),
            "effective_date": str(r.get("effective_date") or ""),
            "run_id": str(r.get("run_id") or ""),
        }
        for r in top
    ]
    return docs, metas
