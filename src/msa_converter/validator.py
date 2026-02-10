"""Data validation and warning/error reporting."""

import sys
from dataclasses import dataclass, field

import pandas as pd

from msa_converter.mappings import MSA_CATEGORY_CODES
from msa_converter.models import TOTRecord, BIDRecord, SIDRecord, PURRecord


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def report(self) -> None:
        """Print validation results to stderr."""
        for w in self.warnings:
            print(f"WARNING: {w}", file=sys.stderr)
        for e in self.errors:
            print(f"ERROR: {e}", file=sys.stderr)
        if self.is_valid:
            print(f"Validation passed ({len(self.warnings)} warnings)", file=sys.stderr)
        else:
            print(f"Validation failed ({len(self.errors)} errors, {len(self.warnings)} warnings)", file=sys.stderr)


REQUIRED_COLUMNS = [
    "CustomerNumber", "CustomerName", "Date", "Address", "City", "State",
    "Zip", "ItemCode", "ItemDescription", "UPCCode", "Qty",
    "OnHandInventory", "Categories", "Promo", "CashCarry", "unit",
]


def validate_input(df: pd.DataFrame) -> ValidationResult:
    """Validate the input DataFrame before building records."""
    result = ValidationResult()

    # Check required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        result.errors.append(f"Missing required columns: {', '.join(missing)}")
        return result  # Can't continue without required columns

    # Check for empty values in key fields
    for col in ["CustomerNumber", "ItemCode", "UPCCode", "Qty"]:
        blanks = df[col].isna() | (df[col].astype(str).str.strip() == "")
        if blanks.any():
            result.errors.append(f"{blanks.sum()} rows have blank {col}")

    # Validate categories map to known MSA codes
    unknown = set(df["Categories"].unique()) - set(MSA_CATEGORY_CODES.keys())
    if unknown:
        result.errors.append(f"Unknown categories (no MSA code mapping): {', '.join(sorted(unknown))}")

    # Validate Qty is numeric
    try:
        pd.to_numeric(df["Qty"])
    except (ValueError, TypeError):
        result.errors.append("Qty column contains non-numeric values")

    # Validate dates are parseable
    from msa_converter.formatter import fmt_date
    bad_dates = []
    for date_val in df["Date"].unique():
        try:
            fmt_date(str(date_val))
        except ValueError:
            bad_dates.append(str(date_val))
    if bad_dates:
        result.errors.append(f"Unparseable dates: {', '.join(bad_dates)}")

    # Warn on UPC length
    upc_lengths = df["UPCCode"].astype(str).str.len()
    short_upcs = upc_lengths[upc_lengths < 12]
    if len(short_upcs) > 0:
        result.warnings.append(f"{len(short_upcs)} rows have UPC codes shorter than 12 digits")

    long_upcs = upc_lengths[upc_lengths > 14]
    if len(long_upcs) > 0:
        result.warnings.append(f"{len(long_upcs)} rows have UPC codes longer than 14 digits")

    return result


def validate_output(
    bids: list[BIDRecord],
    sids: list[SIDRecord],
    purs: list[PURRecord],
    tot: TOTRecord,
) -> ValidationResult:
    """Validate built records against TOT control totals."""
    result = ValidationResult()

    if tot.bid_count != len(bids):
        result.errors.append(f"TOT bid_count ({tot.bid_count}) != actual BID records ({len(bids)})")

    if tot.sid_count != len(sids):
        result.errors.append(f"TOT sid_count ({tot.sid_count}) != actual SID records ({len(sids)})")

    if tot.pur_count != len(purs):
        result.errors.append(f"TOT pur_count ({tot.pur_count}) != actual PUR records ({len(purs)})")

    actual_qty = sum(p.quantity for p in purs)
    if abs(tot.total_quantity - actual_qty) > 0.01:
        result.errors.append(f"TOT total_quantity ({tot.total_quantity}) != sum of PUR quantities ({actual_qty})")

    actual_inv = sum(b.inventory for b in bids)
    if abs(tot.total_inventory - actual_inv) > 0.01:
        result.errors.append(f"TOT total_inventory ({tot.total_inventory}) != sum of BID inventories ({actual_inv})")

    # Validate line widths
    for i, bid in enumerate(bids):
        line = bid.to_line()
        if len(line) != 261:
            result.errors.append(f"BID record {i} has width {len(line)}, expected 261")

    for i, sid in enumerate(sids):
        line = sid.to_line()
        if len(line) != 551:
            result.errors.append(f"SID record {i} has width {len(line)}, expected 551")

    for i, pur in enumerate(purs):
        line = pur.to_line()
        if len(line) != 130:
            result.errors.append(f"PUR record {i} has width {len(line)}, expected 130")

    return result
