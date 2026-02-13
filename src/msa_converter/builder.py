"""Builds MSA MultiCat records from a normalized DataFrame."""

from datetime import datetime, timedelta

import pandas as pd

from msa_converter.config import DistributorConfig
from msa_converter.formatter import fmt_date
from msa_converter.mappings import MSA_CATEGORY_CODES, YES_NO_MAP
from msa_converter.models import HIDRecord, BIDRecord, SIDRecord, PURRecord, TOTRecord


def _week_end_date(dates: pd.Series) -> str:
    """Compute the Saturday week-end date from the max date in the data."""
    max_date = pd.to_datetime(dates).max()
    days_until_saturday = (5 - max_date.weekday()) % 7
    if days_until_saturday == 0 and max_date.weekday() != 5:
        days_until_saturday = 7
    saturday = max_date + timedelta(days=days_until_saturday)
    return saturday.strftime("%Y%m%d")


def _build_sid_lookup(df: pd.DataFrame) -> dict[tuple, str]:
    """Build a mapping from (CustomerNumber, CustomerName, Address, City, State, Zip)
    to a sequential shipping number per customer.

    Returns dict mapping location tuple -> shipping number string.
    """
    locations = (
        df[["CustomerNumber", "CustomerName", "Address", "City", "State", "Zip"]]
        .drop_duplicates()
        .sort_values(["CustomerNumber", "Address"])
    )

    lookup = {}
    customer_seq: dict[str, int] = {}

    for _, row in locations.iterrows():
        cust = row["CustomerNumber"]
        key = (cust, row["CustomerName"], row["Address"], row["City"], str(row["State"]), str(row["Zip"]))
        seq = customer_seq.get(cust, 0) + 1
        customer_seq[cust] = seq
        lookup[key] = str(seq).zfill(8)

    return lookup


def build_records(
    df: pd.DataFrame, config: DistributorConfig
) -> tuple[HIDRecord, list[BIDRecord], list[SIDRecord], list[PURRecord], TOTRecord]:
    """Build all MSA MultiCat records from the input DataFrame."""

    end_date = _week_end_date(df["Date"])
    creation_date = datetime.now().strftime("%Y%m%d")
    sid_lookup = _build_sid_lookup(df)

    # --- BID records: one per unique SKU ---
    bid_records = []
    sku_groups = df.groupby("ItemCode")
    for sku, group in sku_groups:
        row = group.iloc[0]
        category = str(row["Categories"])
        msa_code = MSA_CATEGORY_CODES.get(category, "")
        promo_values = group["Promo"].map(YES_NO_MAP)
        has_promo = "Y" if "Y" in promo_values.values else "N"
        inventory = group["OnHandInventory"].max()

        bid_records.append(BIDRecord(
            upc=str(int(row["UPCCode"])) if pd.notna(row["UPCCode"]) else "",
            sku=str(sku),
            product_description=str(row["ItemDescription"]),
            items_per_selling_unit=str(int(row["unit"])),
            unit_size_description=str(row.get("SellingUnit", "")),
            promotion_indicator=has_promo,
            mfr_product_id=str(int(row["UPCCode"])) if pd.notna(row["UPCCode"]) else "",
            msa_category_code=msa_code,
            inventory=float(inventory),
        ))

    # --- SID records: one per unique customer location ---
    sid_records = []
    for location_key, shipping_number in sid_lookup.items():
        cust_num, cust_name, address, city, state, zip_code = location_key

        # Get first matching row for additional fields
        mask = (
            (df["CustomerNumber"] == cust_num)
            & (df["Address"] == address)
            & (df["City"] == city)
        )
        row = df[mask].iloc[0]

        sid_records.append(SIDRecord(
            customer_number=cust_num,
            shipping_number=shipping_number,
            customer_name=cust_name,
            address=address,
            city=city,
            state=str(state),
            zip_code=str(zip_code),
            country="USA",
            class_of_trade=str(row["ClassOfTrade"]),
            cash_carry_indicator=YES_NO_MAP.get(str(row["CashCarry"]), "N"),
        ))

    # --- PUR records: one per (customer+location, SKU), aggregate qty ---
    pur_records = []
    for location_key, shipping_number in sid_lookup.items():
        cust_num, cust_name, address, city, state, zip_code = location_key

        mask = (
            (df["CustomerNumber"] == cust_num)
            & (df["Address"] == address)
            & (df["City"] == city)
        )
        location_rows = df[mask]

        sku_agg = location_rows.groupby("ItemCode").agg(
            Qty=("Qty", "sum"),
            Date=("Date", "max"),
            Invoice=("Invoice", "first"),
        )

        for sku, agg in sku_agg.iterrows():
            pur_records.append(PURRecord(
                customer_number=cust_num,
                shipping_number=shipping_number,
                sku=str(sku),
                invoice_number=str(agg["Invoice"]),
                transaction_date=fmt_date(str(agg["Date"])),
                quantity=float(agg["Qty"]),
            ))

    # --- HID record ---
    hid = HIDRecord(
        distributor_id=config.distributor_id,
        test_flag="T" if config.test_mode else " ",
        end_date=end_date,
        distributor_name=config.name,
        distributor_address=config.address,
        distributor_city=config.city,
        distributor_state=config.state,
        distributor_zip=config.zip_code,
        distributor_country=config.country,
        contact_last_name=config.contact_last_name,
        contact_first_name=config.contact_first_name,
        contact_phone=config.contact_phone,
        contact_fax=config.contact_fax,
        contact_email=config.contact_email,
        pur_measure_count="0001",
        creation_date=creation_date,
    )

    # --- TOT record ---
    tot = TOTRecord(
        distributor_id=config.distributor_id,
        end_date=end_date,
        bid_count=len(bid_records),
        sid_count=len(sid_records),
        pur_count=len(pur_records),
        total_quantity=sum(p.quantity for p in pur_records),
        total_inventory=sum(b.inventory for b in bid_records),
    )

    return hid, bid_records, sid_records, pur_records, tot
