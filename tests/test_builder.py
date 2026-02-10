"""Tests for record building from input data."""

import pandas as pd
import pytest

from msa_converter.builder import build_records, _week_end_date, _build_sid_lookup
from msa_converter.config import DistributorConfig


@pytest.fixture
def sample_df():
    """Minimal DataFrame mimicking normalized CSV input."""
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
            "CustomerNumber": "C04002", "CustomerName": "J & V WHOLESALE",
            "Date": "1/16/2026", "Address": "2208 Pine Street", "City": "Ceres",
            "State": "CA", "Zip": "95307", "Invoice": "INV/2026/00179",
            "ItemCode": "SMO100BX", "ItemDescription": "Clipper Large Cigar Smooth",
            "MSA": "Yes", "UPCCode": 812615006701, "Qty": 300,
            "OnHandInventory": 2000, "Categories": "Cigars", "Promo": "No",
            "ClassOfTrade": "WHOLESALE", "CashCarry": "No", "unit": 200,
            "SellingUnit": "CARTON", "STICKS": "Sticks",
        },
        {
            "CustomerNumber": "C03218", "CustomerName": "GLOBAL TOBACCO LLC",
            "Date": "1/14/2026", "Address": "2861 CONGRESSMAN LN", "City": "DALLAS",
            "State": "TX", "Zip": "75220", "Invoice": "INV/2026/00169",
            "ItemCode": "FF100B", "ItemDescription": "Clipper Large Cigar",
            "MSA": "Yes", "UPCCode": 812615006700, "Qty": 100,
            "OnHandInventory": 5983, "Categories": "Cigars", "Promo": "Yes",
            "ClassOfTrade": "WHOLESALE", "CashCarry": "No", "unit": 200,
            "SellingUnit": "CARTON", "STICKS": "Sticks",
        },
    ])


@pytest.fixture
def config():
    return DistributorConfig(
        distributor_id="10094001",
        name="TEST DIST",
        state="CA",
    )


class TestWeekEndDate:
    def test_friday_to_saturday(self):
        dates = pd.Series(["1/16/2026"])  # Friday
        assert _week_end_date(dates) == "20260117"

    def test_saturday_stays(self):
        dates = pd.Series(["1/17/2026"])  # Saturday
        assert _week_end_date(dates) == "20260117"

    def test_sunday_to_next_saturday(self):
        dates = pd.Series(["1/18/2026"])  # Sunday
        assert _week_end_date(dates) == "20260124"

    def test_uses_max_date(self):
        dates = pd.Series(["1/12/2026", "1/14/2026", "1/16/2026"])
        assert _week_end_date(dates) == "20260117"


class TestSidLookup:
    def test_single_location_per_customer(self, sample_df):
        lookup = _build_sid_lookup(sample_df)
        # C04002 has 1 location, C03218 has 1 location
        assert len(lookup) == 2

    def test_shipping_numbers_are_sequential(self, sample_df):
        lookup = _build_sid_lookup(sample_df)
        shipping_numbers = set(lookup.values())
        assert "00000001" in shipping_numbers

    def test_multiple_locations_same_customer(self):
        df = pd.DataFrame([
            {"CustomerNumber": "C04002", "CustomerName": "STORE A",
             "Address": "100 Main St", "City": "Ceres", "State": "CA", "Zip": "95307"},
            {"CustomerNumber": "C04002", "CustomerName": "STORE B",
             "Address": "200 Oak Ave", "City": "Fresno", "State": "CA", "Zip": "93727"},
        ])
        lookup = _build_sid_lookup(df)
        assert len(lookup) == 2
        numbers = sorted(lookup.values())
        assert numbers == ["00000001", "00000002"]


class TestBuildRecords:
    def test_record_counts(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        assert len(bids) == 2   # FF100B and SMO100BX
        assert len(sids) == 2   # C04002/Ceres and C03218/Dallas
        assert len(purs) == 3   # FF100B->C04002, SMO100BX->C04002, FF100B->C03218

    def test_tot_counts_match(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        assert tot.bid_count == len(bids)
        assert tot.sid_count == len(sids)
        assert tot.pur_count == len(purs)

    def test_tot_quantity_sum(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        assert tot.total_quantity == pytest.approx(570 + 300 + 100)

    def test_tot_inventory_sum(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        # FF100B inventory=5983 (max), SMO100BX inventory=2000
        assert tot.total_inventory == pytest.approx(5983 + 2000)

    def test_hid_fields(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        assert hid.distributor_id == "10094001"
        assert hid.end_date == "20260117"
        assert hid.test_flag == "T"
        assert hid.distributor_name == "TEST DIST"

    def test_bid_category_mapping(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        for bid in bids:
            assert bid.msa_category_code == "003251"  # Cigars

    def test_bid_promo_indicator(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        # FF100B has both Yes and No promo rows -> Y
        ff100b = [b for b in bids if b.sku == "FF100B"][0]
        assert ff100b.promotion_indicator == "Y"
        # SMO100BX only has No -> N
        smo = [b for b in bids if b.sku == "SMO100BX"][0]
        assert smo.promotion_indicator == "N"

    def test_sid_cash_carry(self, sample_df, config):
        hid, bids, sids, purs, tot = build_records(sample_df, config)
        for sid in sids:
            assert sid.cash_carry_indicator == "N"

    def test_live_mode(self, sample_df):
        config = DistributorConfig(test_mode=False)
        hid, *_ = build_records(sample_df, config)
        assert hid.test_flag == " "
