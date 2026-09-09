from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import DOCUMENT_COUNTS, LANGUAGE_RATIOS, NOISE_RATIOS

def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        return []

    if text.startswith("["):
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed

    return [json.loads(line) for line in text.splitlines() if line.strip()]

def expected_counts(total, ratios):
    raw = {k: total*v for k,v in ratios.items()}
    vals = {k: int(v) for k,v in raw.items()}
    for k in sorted(raw, key=lambda x: raw[x]-vals[x], reverse=True)[:total-sum(vals.values())]:
        vals[k] += 1
    return vals

def validate(path, expected_total=None):
    records = read_jsonl(path)
    total = len(records)
    expected_total = expected_total or (2000 if total == 2000 else total)
    errors = []

    if total != expected_total:
        errors.append(f"record count: expected {expected_total}, got {total}")

    ids = [r.get("document_id") for r in records]
    if any(not x for x in ids):
        errors.append("one or more missing document_id values")
    if len(ids) != len(set(ids)):
        errors.append("duplicate document_id values")

    required = [
        "document_id","document_type","source_type","file_path","file_format",
        "language","page_count","ocr_text","document_number",
        "registration_number","survey_number","subdivision_number","person_names",
        "district","taluka","village","issue_date","registration_date",
        "transaction_date","issuer","document_status","expected_entities",
        "expected_dates","expected_numbers","ground_truth_json",
        "document_payload","data_origin"
    ]
    for i, r in enumerate(records, 1):
        missing = [k for k in required if k not in r]
        if missing:
            errors.append(f"record {i}: missing fields {missing}")
        if r.get("data_origin") != "synthetic":
            errors.append(f"record {i}: data_origin is not synthetic")
        if not isinstance(r.get("ocr_text"), str) or not r["ocr_text"].strip():
            errors.append(f"record {i}: empty ocr_text")
        if r.get("ground_truth_json", {}).get("survey_number") != r.get("survey_number"):
            errors.append(f"record {i}: survey_number ground-truth mismatch")
        if r.get("ground_truth_json", {}).get("document_number") != r.get("document_number"):
            errors.append(f"record {i}: document_number ground-truth mismatch")

    doc_counts = Counter(r.get("document_type") for r in records)
    lang_counts = Counter(r.get("language") for r in records)

    target_docs = DOCUMENT_COUNTS if total == 2000 else expected_counts(total, {k:v/2000 for k,v in DOCUMENT_COUNTS.items()})
    target_lang = expected_counts(total, LANGUAGE_RATIOS)

    if doc_counts != Counter(target_docs):
        errors.append(f"document-type distribution mismatch: {dict(doc_counts)} vs {target_docs}")
    if lang_counts != Counter(target_lang):
        errors.append(f"language distribution mismatch: {dict(lang_counts)} vs {target_lang}")

    report = {
        "valid": not errors,
        "total_records": total,
        "document_counts": dict(doc_counts),
        "expected_document_counts": target_docs,
        "language_counts": dict(lang_counts),
        "expected_language_counts": target_lang,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dataset")
    p.add_argument("--count", type=int, default=None)
    args = p.parse_args()
    raise SystemExit(validate(args.dataset, args.count))
