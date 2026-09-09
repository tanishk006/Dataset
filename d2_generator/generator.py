from __future__ import annotations

import argparse
import json
import math
import random
import re
from datetime import date, timedelta
from pathlib import Path

from config import (
    DOCUMENT_COUNTS, LANGUAGE_RATIOS, NOISE_RATIOS, DEFAULT_CONFLICT_RATE,
    FIRST_NAMES, LAST_NAMES, LOCATIONS, ISSUERS, STATUSES, MARATHI
)

OUT_FIELDS = [
    "document_id", "document_type", "source_type", "file_path", "file_format",
    "language", "page_count", "ocr_text", "document_number",
    "registration_number", "survey_number", "subdivision_number", "person_names",
    "district", "taluka", "village", "issue_date", "registration_date",
    "transaction_date", "issuer", "document_status", "expected_entities",
    "expected_dates", "expected_numbers", "ground_truth_json",
    "document_payload", "data_origin"
]

def allocate_exact(total: int, ratios: dict[str, float]) -> dict[str, int]:
    raw = {k: total * v for k, v in ratios.items()}
    result = {k: math.floor(v) for k, v in raw.items()}
    remaining = total - sum(result.values())
    order = sorted(raw, key=lambda k: raw[k] - result[k], reverse=True)
    for k in order[:remaining]:
        result[k] += 1
    return result

def make_names(rng: random.Random, n=2):
    return [f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}" for _ in range(n)]

def iso(d):
    return d.isoformat() if d else None

def make_base_records(count: int, rng: random.Random):
    if count == 2000:
        types = [t for t, n in DOCUMENT_COUNTS.items() for _ in range(n)]
    else:
        counts = allocate_exact(count, {k: v / 2000 for k, v in DOCUMENT_COUNTS.items()})
        types = [t for t, n in counts.items() for _ in range(n)]

    rng.shuffle(types)

    # Create a parcel registry so related documents can share facts.
    parcel_count = max(1, int(count * 0.60))
    parcels = {}
    for i in range(1, parcel_count + 1):
        district, taluka, village = rng.choice(LOCATIONS)
        survey = f"{rng.randint(10,999)}/{rng.randint(1,9)}{rng.choice(['A','B','C',''])}"
        subdivision = f"{rng.randint(1,9):02d}"
        parcels[i] = {
            "parcel_id": f"BF-PARCEL-{i:06d}",
            "survey_number": survey,
            "subdivision_number": subdivision,
            "district": district,
            "taluka": taluka,
            "village": village,
            "names": make_names(rng, 2),
        }

    records = []
    for idx, doc_type in enumerate(types, 1):
        parcel = parcels[((idx - 1) % parcel_count) + 1]
        base_date = date(2022, 1, 1) + timedelta(days=rng.randint(0, 1500))
        transaction_date = base_date if doc_type in {
            "Sale Deed", "Mutation Document", "Registration Document",
            "Compensation Document", "Award Document", "Possession Document"
        } else None
        registration_date = (
            base_date + timedelta(days=rng.randint(1, 45))
            if doc_type in {"Sale Deed", "Registration Document", "Mutation Document"}
            else None
        )

        # Status and issuer are selected independently.
        issuer = rng.choice(ISSUERS)
        status = rng.choice(STATUSES)

        people = list(parcel["names"])
        if doc_type == "Sale Deed":
            people = make_names(rng, 2)  # seller/buyer; parcel facts remain stable
        elif doc_type == "Death Certificate":
            people = [rng.choice(parcel["names"]), make_names(rng, 1)[0]]
        elif doc_type == "Legal-Heir/Succession":
            people = parcel["names"] + [make_names(rng, 1)[0]]

        rec = {
            "document_id": f"BF-DOC-{idx:06d}",
            "document_type": doc_type,
            "source_type": "synthetic_text",
            "file_path": None,
            "file_format": "TEXT",
            "language": None,
            "page_count": rng.choice([1, 1, 1, 2]),
            "ocr_text": None,
            "document_number": f"{doc_type[:3].upper().replace('/','')}-{base_date.year}-{rng.randint(1,99999):05d}",
            "registration_number": (
                f"REG-{base_date.year}-{rng.randint(1,99999):05d}"
                if doc_type in {"Sale Deed", "Registration Document", "Mutation Document"}
                else None
            ),
            "survey_number": parcel["survey_number"],
            "subdivision_number": parcel["subdivision_number"],
            "person_names": people,
            "district": parcel["district"],
            "taluka": parcel["taluka"],
            "village": parcel["village"],
            "issue_date": iso(base_date),
            "registration_date": iso(registration_date),
            "transaction_date": iso(transaction_date),
            "issuer": issuer,
            "document_status": status,
            "expected_entities": [],
            "expected_dates": [],
            "expected_numbers": [],
            "ground_truth_json": {},
            "document_payload": {},
            "data_origin": "synthetic",
            "_parcel_id": parcel["parcel_id"],
        }
        records.append(rec)
    return records

def render_en(r):
    t = r["document_type"]
    n = ", ".join(r["person_names"])
    common = (
        f"Document Number: {r['document_number']}\n"
        f"Survey Number: {r['survey_number']}\n"
        f"Subdivision: {r['subdivision_number']}\n"
        f"Names: {n}\n"
        f"Village: {r['village']}\n"
        f"Taluka: {r['taluka']}\n"
        f"District: {r['district']}\n"
        f"Issue Date: {r['issue_date']}\n"
        f"Issuer: {r['issuer']}\n"
        f"Status: {r['document_status']}\n"
    )
    if t == "Sale Deed":
        return f"SALE DEED\n{common}Registration Number: {r['registration_number']}\nTransaction Date: {r['transaction_date']}\nSeller and buyer details are recorded for the property described above.\n"
    if t == "Court Order":
        return f"COURT ORDER\n{common}Order Date: {r['issue_date']}\nThe order records the matter concerning the land identified above.\n"
    if t == "Death Certificate":
        return f"DEATH CERTIFICATE\n{common}The certificate records a death-related entry associated with the named persons.\n"
    if t == "Legal-Heir/Succession":
        return f"LEGAL-HEIR / SUCCESSION RECORD\n{common}The record lists persons associated with succession for the property.\n"
    return f"{t.upper()}\n{common}This synthetic record describes the land/document information listed above.\n"

def render_mr(r):
    t = r["document_type"]
    names = ", ".join(r["person_names"])
    return (
        f"{MARATHI.get('document', 'दस्तऐवज')} प्रकार: {t}\n"
        f"{MARATHI['document']}: {r['document_number']}\n"
        f"{MARATHI['survey']}: {r['survey_number']}\n"
        f"{MARATHI['subdivision']}: {r['subdivision_number']}\n"
        f"{MARATHI['holder']}: {names}\n"
        f"{MARATHI['village']}: {r['village']}\n"
        f"{MARATHI['taluka']}: {r['taluka']}\n"
        f"{MARATHI['district']}: {r['district']}\n"
        f"{MARATHI['issue_date']}: {r['issue_date']}\n"
        f"{MARATHI['issuer']}: {r['issuer']}\n"
        f"{MARATHI['status']}: {r['document_status']}\n"
        f"ही नोंद कृत्रिम असून केवळ डेटासेट निर्मितीसाठी आहे.\n"
    )

def render_bilingual(r):
    return (
        f"{r['document_type']} / दस्तऐवज प्रकार\n"
        f"Document No. / दस्तऐवज क्रमांक: {r['document_number']}\n"
        f"Survey No. / सर्वे क्रमांक: {r['survey_number']}\n"
        f"Subdivision / उपविभाग: {r['subdivision_number']}\n"
        f"Names / नावे: {', '.join(r['person_names'])}\n"
        f"Village / गाव: {r['village']}\n"
        f"Taluka / तालुका: {r['taluka']}\n"
        f"District / जिल्हा: {r['district']}\n"
        f"Issue Date / जारी दिनांक: {r['issue_date']}\n"
        f"Issuer / जारी करणारे कार्यालय: {r['issuer']}\n"
        f"Status / स्थिती: {r['document_status']}\n"
        f"This is synthetic dataset content / हा कृत्रिम डेटासेट मजकूर आहे.\n"
    )

def corrupt_ocr(text: str, rng: random.Random):
    substitutions = {
        "Number": ["Nurnber", "Numher", "Nurnber"],
        "Document": ["Docurnent", "Documcnt"],
        "Survey": ["Survcy", "Surv3y"],
        "District": ["Distrlct", "Districf"],
        "Village": ["Vlllage", "Villagc"],
        "Registration": ["Registratlon", "Reglstration"],
        "Date": ["Datc", "Dale"],
    }
    for src, variants in substitutions.items():
        if rng.random() < 0.35:
            text = text.replace(src, rng.choice(variants), 1)

    chars = list(text)
    candidates = [i for i, c in enumerate(chars) if c.isalnum()]
    for i in rng.sample(candidates, min(max(1, len(candidates)//120), len(candidates))):
        if chars[i].isalpha() and rng.random() < 0.5:
            chars[i] = chars[i].swapcase()
        elif chars[i].isdigit() and rng.random() < 0.4:
            chars[i] = rng.choice("0123456789")
    return "".join(chars)

def formatting_variation(text, rng):
    lines = text.splitlines()
    out = []
    for line in lines:
        if rng.random() < 0.35:
            line = line.replace(": ", " : ")
        if rng.random() < 0.20:
            line = "  " + line
        out.append(line)
        if rng.random() < 0.12:
            out.append("")
    return "\n".join(out)

def low_quality(text, rng):
    text = text.replace("\n", " \n ")
    if rng.random() < 0.7:
        text = re.sub(r" {2,}", " ", text)
    if rng.random() < 0.5:
        text = text.replace("/", " / ")
    return corrupt_ocr(text, rng)

def missing_fields(text, rng):
    lines = text.splitlines()
    keep = []
    field_lines = {"Survey Number", "Survey No.", "Village", "Taluka", "District",
                   "Issue Date", "Names", "Document Number", "Registration Number"}
    for line in lines:
        if any(line.startswith(x) for x in field_lines) and rng.random() < 0.20:
            continue
        keep.append(line)
    return "\n".join(keep)

def make_ground_truth(r):
    gt = {
        "document_type": r["document_type"],
        "document_number": r["document_number"],
        "registration_number": r["registration_number"],
        "survey_number": r["survey_number"],
        "subdivision_number": r["subdivision_number"],
        "person_names": r["person_names"],
        "district": r["district"],
        "taluka": r["taluka"],
        "village": r["village"],
        "issue_date": r["issue_date"],
        "registration_date": r["registration_date"],
        "transaction_date": r["transaction_date"],
        "issuer": r["issuer"],
        "document_status": r["document_status"],
    }
    r["ground_truth_json"] = gt
    r["expected_entities"] = [
        {"type": "document_type", "value": r["document_type"]},
        *[{"type": "person_name", "value": x} for x in r["person_names"]],
        {"type": "location", "value": r["village"]},
        {"type": "location", "value": r["taluka"]},
        {"type": "location", "value": r["district"]},
    ]
    r["expected_dates"] = [x for x in [r["issue_date"], r["registration_date"], r["transaction_date"]] if x]
    r["expected_numbers"] = [x for x in [
        r["document_number"], r["registration_number"], r["survey_number"], r["subdivision_number"]
    ] if x]
    r["document_payload"] = {
        "parcel_id": r["_parcel_id"],
        "source_facts": gt,
        "synthetic_only": True,
    }

def generate(count: int, seed: int, output: Path, conflict_rate: float = DEFAULT_CONFLICT_RATE, pretty: bool = False):
    rng = random.Random(seed)
    records = make_base_records(count, rng)

    language_counts = allocate_exact(count, LANGUAGE_RATIOS)
    noise_counts = allocate_exact(count, NOISE_RATIOS)
    languages = [k for k, n in language_counts.items() for _ in range(n)]
    noises = [k for k, n in noise_counts.items() for _ in range(n)]
    rng.shuffle(languages)
    rng.shuffle(noises)

    for r, language, noise in zip(records, languages, noises):
        r["language"] = language
        r["_noise_category"] = noise

        if language == "English":
            clean = render_en(r)
        elif language == "Marathi":
            clean = render_mr(r)
        else:
            clean = render_bilingual(r)

        make_ground_truth(r)

        if noise == "Clean OCR":
            ocr = clean
        elif noise == "Formatting variation":
            ocr = formatting_variation(clean, rng)
        elif noise == "OCR character noise":
            ocr = corrupt_ocr(clean, rng)
        elif noise == "Missing fields":
            ocr = missing_fields(clean, rng)
        elif noise == "Low-quality scan":
            ocr = low_quality(clean, rng)
        else:
            # The noise bucket changes language presentation while retaining the
            # structured language label and source facts.
            if language == "English":
                ocr = render_bilingual(r)
            elif language == "Marathi":
                ocr = render_bilingual(r)
            else:
                ocr = render_en(r) if rng.random() < 0.5 else render_mr(r)

        # Optional deliberate conflict support. No "correct" source is encoded.
        if conflict_rate > 0 and rng.random() < conflict_rate:
            r["document_payload"]["conflict"] = {
                "present": True,
                "statement": "Sources disagree; legal correctness is intentionally unresolved."
            }

        r["ocr_text"] = ocr

        for k in OUT_FIELDS:
            if k not in r:
                r[k] = None

        # Internal-only fields are removed from the final record.
        r.pop("_parcel_id", None)
        r.pop("_noise_category", None)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        if pretty:
            data = [{k: r[k] for k in OUT_FIELDS} for r in records]
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            for r in records:
                record = {k: r[k] for k in OUT_FIELDS}
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return records

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="../output/dataset.jsonl")
    parser.add_argument("--conflict-rate", type=float, default=DEFAULT_CONFLICT_RATE)
    parser.add_argument("--pretty", action="store_true", help="Write a readable pretty-printed JSON array instead of compact JSONL.")
    args = parser.parse_args()
    if args.count < 1:
        raise SystemExit("count must be positive")
    if not 0 <= args.conflict_rate <= 1:
        raise SystemExit("conflict-rate must be between 0 and 1")
    generate(args.count, args.seed, Path(args.output), args.conflict_rate, args.pretty)
    mode = "pretty JSON array" if args.pretty else "compact JSONL"
    print(f"Generated {args.count} records -> {args.output} ({mode})")
