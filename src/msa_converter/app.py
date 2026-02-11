"""Streamlit web UI for MSA MultiCat converter."""

import streamlit as st

from msa_converter.builder import build_records
from msa_converter.config import DistributorConfig
from msa_converter.reader import read_input
from msa_converter.validator import validate_input, validate_output
from msa_converter.writer import write_msa_bytes

st.set_page_config(page_title="MSA MultiCat Converter", layout="wide")
st.title("MSA MultiCat Converter")

# --- Sidebar: Distributor Config ---
with st.sidebar:
    st.header("Distributor Info")
    distributor_id = st.text_input("Distributor ID", value="10094001", max_chars=8)
    name = st.text_input("Company Name", max_chars=32)
    address = st.text_input("Address", max_chars=90)
    city = st.text_input("City", max_chars=25)
    state = st.text_input("State", max_chars=2)
    zip_code = st.text_input("Zip Code", max_chars=9)
    country = st.text_input("Country", value="USA", max_chars=3)

    st.subheader("Contact")
    contact_first = st.text_input("First Name", max_chars=20)
    contact_last = st.text_input("Last Name", max_chars=20)
    contact_phone = st.text_input("Phone", max_chars=10)
    contact_email = st.text_input("Email", max_chars=60)

    st.divider()
    test_mode = st.toggle("Test Mode", value=True)

# --- Main Area ---
uploaded = st.file_uploader("Upload sales file", type=["csv", "xls", "xlsx"])

if uploaded and st.button("Convert", type="primary"):
    config = DistributorConfig(
        distributor_id=distributor_id,
        name=name,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        country=country,
        contact_last_name=contact_last,
        contact_first_name=contact_first,
        contact_phone=contact_phone,
        contact_email=contact_email,
        test_mode=test_mode,
    )

    # Read input
    try:
        df = read_input(uploaded, filename=uploaded.name)
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()

    st.info(f"Loaded {len(df)} MSA-reportable rows")

    # Validate input
    input_result = validate_input(df)
    if input_result.warnings:
        for w in input_result.warnings:
            st.warning(w)
    if not input_result.is_valid:
        for e in input_result.errors:
            st.error(e)
        st.stop()

    # Build records
    try:
        hid, bids, sids, purs, tot = build_records(df, config)
    except Exception as e:
        st.error(f"Failed to build records: {e}")
        st.stop()

    # Validate output
    output_result = validate_output(bids, sids, purs, tot)
    if not output_result.is_valid:
        for e in output_result.errors:
            st.error(e)
        st.stop()

    # Summary
    st.success("Conversion successful!")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("BID Records", len(bids))
    col2.metric("SID Records", len(sids))
    col3.metric("PUR Records", len(purs))
    col4.metric("Total Qty", f"{tot.total_quantity:,.0f}")

    # Generate and offer download
    output_name = uploaded.name.rsplit(".", 1)[0] + ".msa"
    data = write_msa_bytes(hid, bids, sids, purs, tot)
    st.download_button(
        "Download .msa file",
        data=data,
        file_name=output_name,
        mime="application/octet-stream",
    )
