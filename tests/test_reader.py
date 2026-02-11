"""Tests for CSV/XLS input reader."""

from io import BytesIO

import pandas as pd
import pytest

from msa_converter.reader import read_input


@pytest.fixture
def csv_bytes():
    """Minimal CSV content as bytes."""
    content = (
        "CustomerNumber,CustomerName,MSA,Categories\n"
        "C001,ACME,Yes,Cigars\n"
        "C002,BETA,No,Cigarettes\n"
        "C003,GAMMA,Yes,Cigars\n"
    )
    return content.encode("utf-8")


class TestReadInputBytesIO:
    def test_csv_from_bytesio(self, csv_bytes):
        buf = BytesIO(csv_bytes)
        df = read_input(buf, filename="upload.csv")
        # Should filter out the "No" MSA row
        assert len(df) == 2

    def test_csv_from_bytesio_default_format(self, csv_bytes):
        buf = BytesIO(csv_bytes)
        # No filename — defaults to CSV
        df = read_input(buf)
        assert len(df) == 2

    def test_bytesio_with_name_attribute(self, csv_bytes):
        buf = BytesIO(csv_bytes)
        buf.name = "data.csv"
        df = read_input(buf)
        assert len(df) == 2

    def test_column_aliases_applied(self, csv_bytes):
        content = (
            "Customer Number,Customer Name,MSA,Catagories\n"
            "C001,ACME,Yes,Cigars\n"
        )
        buf = BytesIO(content.encode("utf-8"))
        df = read_input(buf)
        assert "CustomerNumber" in df.columns
        assert "CustomerName" in df.columns
        assert "Categories" in df.columns

    def test_whitespace_stripped(self):
        content = (
            "CustomerNumber,CustomerName,MSA,Categories\n"
            "  C001  , ACME ,Yes,  Cigars  \n"
        )
        buf = BytesIO(content.encode("utf-8"))
        df = read_input(buf)
        assert df.iloc[0]["CustomerNumber"] == "C001"
        assert df.iloc[0]["CustomerName"] == "ACME"
        assert df.iloc[0]["Categories"] == "Cigars"

    def test_case_insensitive_aliases(self):
        content = (
            "customer number,CUSTOMER NAME,msa,catagories\n"
            "C001,ACME,Yes,Cigars\n"
        )
        buf = BytesIO(content.encode("utf-8"))
        df = read_input(buf)
        assert "CustomerNumber" in df.columns
        assert "CustomerName" in df.columns
        assert "Categories" in df.columns

    def test_unsupported_format_raises(self, csv_bytes):
        buf = BytesIO(csv_bytes)
        with pytest.raises(ValueError, match="Unsupported"):
            read_input(buf, filename="data.json")
