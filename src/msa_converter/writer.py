"""Writes MSA MultiCat records to a fixed-width .msa file."""

from pathlib import Path

from msa_converter.models import HIDRecord, BIDRecord, SIDRecord, PURRecord, TOTRecord


def write_msa(
    path: str | Path,
    hid: HIDRecord,
    bids: list[BIDRecord],
    sids: list[SIDRecord],
    purs: list[PURRecord],
    tot: TOTRecord,
) -> None:
    """Write all records to a fixed-width ASCII .msa file.

    Record order: HID, all BIDs, all SIDs, all PURs, TOT.
    Lines are terminated with CR+LF per MSA spec.
    """
    path = Path(path)
    with open(path, "w", newline="") as f:
        f.write(hid.to_line() + "\r\n")
        for bid in bids:
            f.write(bid.to_line() + "\r\n")
        for sid in sids:
            f.write(sid.to_line() + "\r\n")
        for pur in purs:
            f.write(pur.to_line() + "\r\n")
        f.write(tot.to_line() + "\r\n")


def write_msa_bytes(
    hid: HIDRecord,
    bids: list[BIDRecord],
    sids: list[SIDRecord],
    purs: list[PURRecord],
    tot: TOTRecord,
) -> bytes:
    """Return MSA file content as bytes (for in-memory downloads)."""
    lines = [hid.to_line()]
    lines.extend(bid.to_line() for bid in bids)
    lines.extend(sid.to_line() for sid in sids)
    lines.extend(pur.to_line() for pur in purs)
    lines.append(tot.to_line())
    return "\r\n".join(lines).encode("ascii") + b"\r\n"
