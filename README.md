# multicat-msa-convertor

Converts CSV/XLS tobacco sales data into MSA MultiCat fixed-width `.msa` files for distributor reporting. Two interfaces are provided: a CLI (`msa-convert`) and a Streamlit web UI.

## Overview

Tobacco distributors are required to submit sales data to the Master Settlement Agreement (MSA) reporting system in a specific fixed-width format called MultiCat. This tool takes raw sales exports (CSV or Excel) and transforms them into valid `.msa` files ready for submission.

The pipeline is: **reader → validator → builder → writer**

1. **Reader** — Loads the CSV/XLS file into a DataFrame, normalizes column names via case-insensitive alias matching, and filters to MSA-reportable rows.
2. **Validator (input)** — Checks for required columns, valid MSA category codes, and parseable dates. Aborts early if the data cannot be processed.
3. **Builder** — Aggregates data into five MSA record types:
   - **HID** — Header (1 per file): distributor identity and submission metadata.
   - **BID** — Brand/item (1 per unique SKU): product details and category codes.
   - **SID** — Ship-to location (1 per unique customer address): retailer address info.
   - **PUR** — Purchase (1 per location × SKU combination): quantity sold, summed across the reporting period.
   - **TOT** — Totals (1 per file): control totals for record counts and quantities.
4. **Validator (output)** — Verifies that built records reconcile against TOT control totals and that every line is the correct fixed width per the MSA spec.
5. **Writer** — Emits the `.msa` file with records in the required order (HID, BIDs, SIDs, PURs, TOT), each line terminated with CR+LF.

## Requirements

- Python 3.10+
- Dependencies: `click`, `pandas`, `xlrd`, `pydantic`, `pyyaml`, `streamlit`

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd multicat-msa-convertor

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Running Locally

### CLI

```bash
# Basic usage (outputs <input_stem>.msa in the same directory)
msa-convert sales.csv

# Specify output path
msa-convert sales.csv -o output.msa

# Use a distributor config file
msa-convert sales.csv -c config.yaml

# Override distributor ID and switch to live (non-test) mode
msa-convert sales.csv --live --distributor-id 10094001

# Run in explicit test mode (default)
msa-convert sales.csv --test
```

### Streamlit Web UI

```bash
streamlit run src/msa_converter/app.py
```

Open your browser to `http://localhost:8501`. Fill in distributor info in the sidebar, upload a CSV/XLS file, and click **Convert** to download the `.msa` file.

### Tests

```bash
# Run all tests
python -m pytest tests/

# Run a specific test file
python -m pytest tests/test_builder.py

# Run a specific test case with verbose output
python -m pytest tests/test_builder.py::TestBuildRecords::test_record_counts -v
```

## Distributor Configuration

Distributor metadata can be supplied via a YAML config file. Copy and edit the example:

```bash
cp config.example.yaml config.yaml
```

```yaml
# config.example.yaml
distributor_id: "10094001"
name: "KARDAL INC DBA MEGAWHOLESALE"
address: "2682 BRENNER DR"
city: "DALLAS"
state: "TX"
zip_code: "75220"
country: "USA"
contact_last_name: "LIM"
contact_first_name: "LIZA"
contact_phone: "8178087618"
contact_email: "Liza@americajuiceco.com"
test_mode: true
```

Pass it to the CLI with `-c config.yaml`. In the web UI, fields are entered directly in the sidebar.

> **Test vs. live mode:** The `T` flag in the HID record signals a test submission. Use `--live` (or toggle off Test Mode in the UI) only when submitting for real.

## Input File Format

Input files must contain columns that map to the following fields (case-insensitive, common aliases are recognized automatically):

| Field | Description |
|---|---|
| SKU / item number | Unique product identifier |
| Brand / product name | Brand and item description |
| MSA category | Maps to a 6-digit MSA category code |
| Customer address, city, state, zip | Ship-to retailer location |
| Date | Sale or invoice date |
| Quantity | Units sold |

Column names are normalized using alias lookup defined in `mappings.py`. If a column name is not recognized, add an alias there.

## Project Structure

```
src/msa_converter/
├── app.py          # Streamlit web UI
├── builder.py      # Aggregates DataFrame into MSA record objects
├── cli.py          # Click CLI entry point
├── config.py       # Pydantic distributor config model
├── formatter.py    # Fixed-width field formatting utilities
├── mappings.py     # Column aliases and MSA category code lookup
├── models.py       # Dataclasses for HID, BID, SID, PUR, TOT records
├── reader.py       # CSV/XLS ingestion and column normalization
├── validator.py    # Input and output validation
└── writer.py       # .msa file writer
tests/              # Pytest test suite
config.example.yaml # Example distributor config
```
