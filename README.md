# multicat-msa-convertor

Converts CSV/XLS tobacco sales data into MSA MultiCat fixed-width `.msa` files for distributor reporting. Supports two interfaces: a CLI (`msa-convert`) and a Streamlit web UI.

## Overview

Tobacco distributors are required to submit weekly sales data to MSA (Management Science Associates) in a proprietary fixed-width format called MultiCat. This tool takes a standard CSV or XLS sales export and produces a spec-compliant `.msa` file ready for submission.

## Pipeline

```
Input (CSV/XLS) → Reader → Validator → Builder → Writer → Output (.msa)
```

1. **Reader** — Loads the CSV/XLS into a DataFrame. Normalises column names via case-insensitive alias matching and filters rows to MSA-reportable items only.
2. **Validator (input)** — Checks required columns are present, categories are valid, and dates are parseable. Aborts with a report if issues are found.
3. **Builder** — Produces five record types from the data:
   - **HID** — One header record per file (distributor metadata, week-end date).
   - **BID** — One brand record per unique SKU.
   - **SID** — One location record per unique customer address.
   - **PUR** — One purchase record per (location, SKU) pair, with quantities summed.
   - **TOT** — One control-total record for validation.
4. **Validator (output)** — Confirms record counts match TOT totals and all lines are the correct fixed width.
5. **Writer** — Writes records in order (HID → BIDs → SIDs → PURs → TOT), lines terminated with CR+LF.

## Requirements

- Python 3.10+

## Installation

```bash
# Clone the repo
git clone https://github.com/davidjmcgovern/multicat-msa-convertor.git
cd multicat-msa-convertor

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Running Locally

### CLI

```bash
# Basic usage (outputs <input_stem>.msa alongside the input file)
msa-convert sales.csv

# Specify output path
msa-convert sales.csv -o output/week42.msa

# Use a distributor config YAML
msa-convert sales.csv -c config.yaml

# Override distributor ID and run in live mode
msa-convert sales.csv --distributor-id 10094001 --live
```

The `--test` flag (default) sets the submission flag to `T`; `--live` sets it to a space for real submissions.

### Streamlit Web UI

```bash
streamlit run src/msa_converter/app.py
```

Open the URL shown in your terminal (typically `http://localhost:8501`). Upload a CSV/XLS file, fill in distributor details via the form, and download the generated `.msa` file.

## Distributor Config YAML

CLI users can supply a YAML file instead of entering details via flags:

```yaml
distributor_id: "10094001"
name: "My Tobacco Dist Co"
address: "123 Main St"
city: "Atlanta"
state: "GA"
zip_code: "30301"
country: "USA"
contact_last_name: "Smith"
contact_first_name: "Jane"
contact_phone: "4045550100"
contact_fax: ""
contact_email: "jane@example.com"
test_mode: true
```

## Running Tests

```bash
# All tests
python -m pytest tests/

# Single file
python -m pytest tests/test_builder.py

# Single test with verbose output
python -m pytest tests/test_builder.py::TestBuildRecords::test_record_counts -v
```
