"""Fixed-width field formatting utilities for MSA MultiCat format."""

from datetime import datetime


def fmt(value: str, width: int, justify: str = "L", fill: str = " ") -> str:
    """Format a value to fixed width.

    Args:
        value: The string value to format.
        width: Target field width.
        justify: "L" for left-justified, "R" for right-justified.
        fill: Fill character, " " (blank) or "0" (zero).

    Returns:
        Fixed-width string, truncated if value exceeds width.
    """
    value = str(value) if value is not None else ""
    if len(value) > width:
        value = value[:width]
    if justify == "L":
        return value.ljust(width, fill)
    return value.rjust(width, fill)


def fmt_date(date_str: str) -> str:
    """Parse a date string to YYYYMMDD format.

    Handles M/D/YYYY and other common formats.
    """
    date_str = str(date_str).strip()
    for date_fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%Y%m%d"):
        try:
            return datetime.strptime(date_str, date_fmt).strftime("%Y%m%d")
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str}")


def fmt_real(value: float, width: int, fill: str = "0") -> str:
    """Format a real number with floating decimal point.

    Per MSA spec, numeric fields are reported as real numbers with
    floating decimal point, right-justified and zero-filled.

    Examples (width=11):
        570   -> "00000570.00"
        1.5   -> "00000001.50"
        -4.0  -> "-0000004.00"
    """
    value = float(value)
    negative = value < 0
    abs_value = abs(value)

    formatted = f"{abs_value:.2f}"

    if negative:
        # Negative sign takes one position from the available width
        return "-" + formatted.rjust(width - 1, fill)
    return formatted.rjust(width, fill)
