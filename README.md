# BhoomiFlow D2 Synthetic Dataset Generator FOR SIH 2026

This project implements a Python-only generator for the supplied D2 specification.

## What it generates

- Structured synthetic facts
- 15 document types with the specified distribution
- English / Marathi / Marathi-English records
- Controlled OCR/noise categories
- Stable `BF-DOC-XXXXXX` IDs
- Ground truth derived from the same structured facts used to render the document
- Cross-document parcel consistency
- Independent issuer/status selection
- Optional unresolved conflict metadata
- JSONL output
- Validation of schema, counts, IDs, and ground-truth consistency

## Important scope decision

The supplied specification does not explicitly require physical PDF/image files. Therefore this first implementation produces JSONL records with `ocr_text` and keeps `file_path` as `null` and `file_format` as `TEXT`.

If the senior later confirms that physical PDFs/images are required, add a rendering stage after the structured generator. Do not change the ground-truth source.

## Run a 50-record test

From the `d2_generator` directory:

```bash
python generator.py --count 50 --seed 42 --output ../output/test_50.jsonl
python validate.py ../output/test_50.jsonl --count 50
```

The 50-record distribution is proportional using deterministic largest-remainder allocation. Exact D2 document counts are enforced when `--count 2000` is used.

## Generate the final D2 dataset

```bash
python generator.py --count 2000 --seed 42 --output ../output/dataset_2000.jsonl
python validate.py ../output/dataset_2000.jsonl --count 2000
```

Expected exact language counts:

- English: 900
- Marathi: 600
- Marathi-English: 500

The six noise buckets are allocated exactly in the generator, but the current validator focuses on schema and core distributions. If your senior requires explicit noise labels in the final schema, add a `noise_category` field only after confirming that schema change is acceptable; otherwise keep it internal.

## Conflict cases

The specification does not give a required percentage. Conflict support is therefore optional:

```bash
python generator.py --count 2000 --seed 42 --conflict-rate 0.03 --output ../output/dataset_conflicts.jsonl
```

A conflict only records that sources disagree; it does not label either source as legally correct.

## Notes

- All records are synthetic.
- No external API or LLM is required.
- The random seed makes generation reproducible.
- This is a dataset generator, not a generator of real government records.
