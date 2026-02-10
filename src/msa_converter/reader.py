"""CSV/XLS input reader with column normalization."""

from pathlib import Path

import pandas as pd

from msa_converter.mappings import COLUMN_ALIASES


def read_input(path: str | Path) -> pd.DataFrame:
    """Read a CSV or XLS file and return a normalized DataFrame.

    - Auto-detects format by file extension
    - Strips whitespace from column headers and string values
    - Renames columns using COLUMN_ALIASES
    - Filters to MSA-reportable rows only (MSA == "Yes")
    """
    path = Path(path)
    ext = path.suffix.lower()

    if ext in (".xls", ".xlsx"):
        df = pd.read_excel(path)
    elif ext == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # Strip whitespace from column headers
    df.columns = df.columns.str.strip()

    # Rename known aliases (e.g. "Catagories" -> "Categories")
    df = df.rename(columns=COLUMN_ALIASES)

    # Strip whitespace from all string columns
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Filter to MSA-reportable rows
    if "MSA" in df.columns:
        before = len(df)
        df = df[df["MSA"].str.lower() == "yes"].copy()
        filtered = before - len(df)
        if filtered > 0:
            print(f"Filtered out {filtered} non-MSA rows ({before} -> {len(df)})")

    return df
