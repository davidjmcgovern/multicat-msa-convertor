# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Converts CSV/XLS tobacco sales data into MSA MultiCat fixed-width `.msa` files for distributor reporting. Two interfaces: CLI (`msa-convert`) and Streamlit web UI.

## Commands

```bash
# Install (editable, with dev deps)
pip install -e ".[dev]"

# Run all tests
python -m pytest tests/

# Run a single test file
python -m pytest tests/test_builder.py

# Run a specific test
python -m pytest tests/test_builder.py::TestBuildRecords::test_record_counts -v

# Run Streamlit app locally
streamlit run src/msa_converter/app.py

# CLI usage
msa-convert input.csv -o output.msa --test --distributor-id 10094001
```

## Architecture

Pipeline: **reader → validator → builder → writer**

- `reader.py` — Reads CSV/XLS into a pandas DataFrame. Normalizes columns via case-insensitive alias lookup (`mappings.py`). Filters to MSA-reportable rows. Accepts file paths or BytesIO (for Streamlit).
- `validator.py` — Two-stage validation: `validate_input()` checks the DataFrame (required columns, valid categories, parseable dates); `validate_output()` checks built records match TOT control totals and have correct line widths.
- `builder.py` — Transforms DataFrame into 5 record types. Key aggregation: BID=1 per unique SKU, SID=1 per unique customer location (address+city+state+zip), PUR=1 per (location, SKU) with summed quantities. Computes week-end date (next Saturday from max date).
- `models.py` — Dataclasses for HID (337), BID (261), SID (551), PUR (130), TOT (140). Each has a `to_line()` method producing fixed-width strings. Column positions are 1-indexed per MSA spec.
- `writer.py` — `write_msa()` writes to file, `write_msa_bytes()` returns bytes. Record order: HID, BIDs, SIDs, PURs, TOT. Lines terminated with CR+LF.
- `formatter.py` — `fmt()` for fixed-width fields (LJ/BF, RJ/ZF), `fmt_date()` for YYYYMMDD, `fmt_real()` for decimal numbers.
- `mappings.py` — `COLUMN_ALIASES` (column name normalization), `MSA_CATEGORY_CODES` (category→6-digit code), `YES_NO_MAP`.
- `config.py` — Pydantic model for distributor metadata. Loaded from YAML or Streamlit form.
- `cli.py` — Click CLI entry point. `app.py` — Streamlit web UI.

## Key Conventions

- Field formatting must match the MSA spec exactly. Justification types: LJ/BF (left-justify/blank-fill), RJ/ZF (right-justify/zero-fill), "Full" (use LJ/BF in code). The spec is at `.specs/Master_MultiCat_Format_Requirements_TOB.pdf`.
- Column alias matching is case-insensitive. New aliases go in `COLUMN_ALIASES` in `mappings.py`.
- `.data/` and `.specs/` are gitignored (contain real sales data and proprietary spec PDFs).
- Default distributor ID is `10094001`. Test mode flag (`T`) is set by default; live mode uses a space character.
- Streamlit Cloud deployment uses `requirements.txt` (not pyproject.toml). Keep both in sync.
