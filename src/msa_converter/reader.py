"""CSV/XLS input reader with column normalization."""

from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

import pandas as pd

from msa_converter.mappings import COLUMN_ALIASES


def read_input(source: Union[str, Path, BinaryIO], filename: str | None = None) -> pd.DataFrame:
    """Read a CSV or XLS file and return a normalized DataFrame.

    - Accepts a file path (str/Path) or a file-like object (BytesIO)
    - For file-like objects, pass `filename` to detect format (defaults to CSV)
    - Auto-detects format by file extension
    - Strips whitespace from column headers and string values
    - Renames columns using COLUMN_ALIASES
    - Filters to MSA-reportable rows only (MSA == "Yes")
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        ext = path.suffix.lower()
        if ext in (".xls", ".xlsx"):
            df = pd.read_excel(path)
        elif ext == ".csv":
            df = pd.read_csv(path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    else:
        # File-like object (e.g. BytesIO from Streamlit upload)
        name = filename or getattr(source, "name", "upload.csv")
        ext = Path(name).suffix.lower()
        if ext in (".xls", ".xlsx"):
            df = pd.read_excel(source)
        elif ext == ".csv":
            df = pd.read_csv(source)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    # Strip whitespace from column headers
    df.columns = df.columns.str.strip()

    # Case-insensitive column alias lookup
    aliases_lower = {k.lower(): v for k, v in COLUMN_ALIASES.items()}
    df = df.rename(columns=lambda c: aliases_lower.get(c.lower(), c))

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
