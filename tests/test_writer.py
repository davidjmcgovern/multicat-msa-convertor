"""End-to-end tests for MSA file writing."""

import os
import tempfile

import pandas as pd
import pytest

from msa_converter.builder import build_records
from msa_converter.config import DistributorConfig
from msa_converter.reader import read_input
from msa_converter.validator import validate_input, validate_output
from msa_converter.writer import write_msa, write_msa_bytes


@pytest.fixture
def config():
    return DistributorConfig(
        distributor_id="10094001",
        name="TEST DIST",
        state="CA",
    )


@pytest.fixture
def sample_df():
    return pd.DataFrame([
        {
            "CustomerNumber": "C04002", "CustomerName": "J & V WHOLESALE",
            "Date": "1/16/2026", "Address": "2208 Pine Street", "City": "Ceres",
            "State": "CA", "Zip": "95307", "Invoice": "INV/2026/00179",
            "ItemCode": "FF100B", "ItemDescription": "Clipper Large Cigar",
            "MSA": "Yes", "UPCCode": 812615006700, "Qty": 570,
            "OnHandInventory": 5983, "Categories": "Cigars", "Promo": "No",
            "ClassOfTrade": "WHOLESALE", "CashCarry": "No", "unit": 200,
            "SellingUnit": "CARTON", "STICKS": "Sticks",
        },
        {
            "CustomerNumber": "C03218", "CustomerName": "GLOBAL TOBACCO LLC",
            "Date": "1/14/2026", "Address": "2861 CONGRESSMAN LN", "City": "DALLAS",
            "State": "TX", "Zip": "75220", "Invoice": "INV/2026/00169",
            "ItemCode": "RD100B", "ItemDescription": "GOLDEN BAY",
            "MSA": "Yes", "UPCCode": 812615006702, "Qty": 100,
            "OnHandInventory": 1000, "Categories": "Cigarettes", "Promo": "No",
            "ClassOfTrade": "WHOLESALE", "CashCarry": "No", "unit": 200,
            "SellingUnit": "CARTON", "STICKS": "Sticks",
        },
    ])


class TestWriteMsa:
    def test_output_file_created(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        with tempfile.NamedTemporaryFile(suffix=".msa", delete=False) as f:
            path = f.name
        try:
            write_msa(path, hid, bids, sids, purs, tot)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_line_count(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        with tempfile.NamedTemporaryFile(suffix=".msa", delete=False) as f:
            path = f.name
        try:
            write_msa(path, hid, bids, sids, purs, tot)
            with open(path, "rb") as f:
                lines = [l for l in f.read().split(b"\r\n") if l]
            expected = 1 + len(bids) + len(sids) + len(purs) + 1
            assert len(lines) == expected
        finally:
            os.unlink(path)

    def test_crlf_line_endings(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        with tempfile.NamedTemporaryFile(suffix=".msa", delete=False) as f:
            path = f.name
        try:
            write_msa(path, hid, bids, sids, purs, tot)
            with open(path, "rb") as f:
                content = f.read()
            # All \n should be preceded by \r
            assert b"\n" not in content.replace(b"\r\n", b"")
        finally:
            os.unlink(path)

    def test_record_widths(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        with tempfile.NamedTemporaryFile(suffix=".msa", delete=False) as f:
            path = f.name
        try:
            write_msa(path, hid, bids, sids, purs, tot)
            with open(path, "rb") as f:
                lines = [l for l in f.read().split(b"\r\n") if l]

            # HID
            assert len(lines[0]) == 337
            assert lines[0][:3] == b"HID"

            # BIDs
            for i in range(1, 1 + len(bids)):
                assert len(lines[i]) == 261
                assert lines[i][:3] == b"BID"

            # SIDs
            sid_start = 1 + len(bids)
            for i in range(sid_start, sid_start + len(sids)):
                assert len(lines[i]) == 551
                assert lines[i][:3] == b"SID"

            # PURs
            pur_start = sid_start + len(sids)
            for i in range(pur_start, pur_start + len(purs)):
                assert len(lines[i]) == 130
                assert lines[i][:3] == b"PUR"

            # TOT
            assert len(lines[-1]) == 140
            assert lines[-1][:3] == b"TOT"
        finally:
            os.unlink(path)

    def test_record_order(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        with tempfile.NamedTemporaryFile(suffix=".msa", delete=False) as f:
            path = f.name
        try:
            write_msa(path, hid, bids, sids, purs, tot)
            with open(path, "rb") as f:
                lines = [l for l in f.read().split(b"\r\n") if l]

            types = [l[:3] for l in lines]
            # Should be HID, then BIDs, then SIDs, then PURs, then TOT
            assert types[0] == b"HID"
            assert types[-1] == b"TOT"
            # All BIDs come before all SIDs
            bid_end = max(i for i, t in enumerate(types) if t == b"BID")
            sid_start = min(i for i, t in enumerate(types) if t == b"SID")
            assert bid_end < sid_start
            # All SIDs come before all PURs
            sid_end = max(i for i, t in enumerate(types) if t == b"SID")
            pur_start = min(i for i, t in enumerate(types) if t == b"PUR")
            assert sid_end < pur_start
        finally:
            os.unlink(path)

    def test_output_validation_passes(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        result = validate_output(bids, sids, purs, tot)
        assert result.is_valid


class TestWriteMsaBytes:
    def test_returns_bytes(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        data = write_msa_bytes(hid, bids, sids, purs, tot)
        assert isinstance(data, bytes)

    def test_crlf_line_endings(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        data = write_msa_bytes(hid, bids, sids, purs, tot)
        assert b"\n" not in data.replace(b"\r\n", b"")

    def test_line_count(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        data = write_msa_bytes(hid, bids, sids, purs, tot)
        lines = [l for l in data.split(b"\r\n") if l]
        assert len(lines) == 1 + len(bids) + len(sids) + len(purs) + 1

    def test_matches_file_output(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        data = write_msa_bytes(hid, bids, sids, purs, tot)
        with tempfile.NamedTemporaryFile(suffix=".msa", delete=False) as f:
            path = f.name
        try:
            write_msa(path, hid, bids, sids, purs, tot)
            with open(path, "rb") as f:
                file_data = f.read()
            assert data == file_data
        finally:
            os.unlink(path)


class TestEndToEnd:
    """End-to-end test using the actual sample data file if available."""

    SAMPLE_CSV = os.path.join(
        os.path.dirname(__file__), "..", ".data", "011726 - 011726.csv"
    )

    @pytest.mark.skipif(
        not os.path.exists(SAMPLE_CSV), reason="Sample CSV not available"
    )
    def test_full_conversion(self):
        config = DistributorConfig(distributor_id="10094001")
        df = read_input(self.SAMPLE_CSV)

        input_result = validate_input(df)
        assert input_result.is_valid

        hid, bids, sids, purs, tot = build_records(df, config)

        output_result = validate_output(bids, sids, purs, tot)
        assert output_result.is_valid

        with tempfile.NamedTemporaryFile(suffix=".msa", delete=False) as f:
            path = f.name
        try:
            write_msa(path, hid, bids, sids, purs, tot)
            with open(path, "rb") as f:
                lines = [l for l in f.read().split(b"\r\n") if l]
            assert len(lines) == 1 + len(bids) + len(sids) + len(purs) + 1
        finally:
            os.unlink(path)
