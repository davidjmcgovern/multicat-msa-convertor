"""Tests for fixed-width field formatting utilities."""

import pytest

from msa_converter.formatter import fmt, fmt_date, fmt_real


class TestFmt:
    def test_left_justify_blank_fill(self):
        assert fmt("ABC", 8) == "ABC     "

    def test_right_justify_zero_fill(self):
        assert fmt("123", 8, justify="R", fill="0") == "00000123"

    def test_right_justify_blank_fill(self):
        assert fmt("ABC", 8, justify="R") == "     ABC"

    def test_left_justify_zero_fill(self):
        assert fmt("12", 6, justify="L", fill="0") == "120000"

    def test_truncation(self):
        assert fmt("TOOLONGVALUE", 8) == "TOOLONGV"

    def test_exact_width(self):
        assert fmt("ABCDEFGH", 8) == "ABCDEFGH"

    def test_empty_string(self):
        assert fmt("", 5) == "     "

    def test_none_value(self):
        assert fmt(None, 5) == "     "


class TestFmtDate:
    def test_slash_format(self):
        assert fmt_date("1/16/2026") == "20260116"

    def test_slash_format_padded(self):
        assert fmt_date("01/03/2024") == "20240103"

    def test_iso_format(self):
        assert fmt_date("2026-01-16") == "20260116"

    def test_invalid_date(self):
        with pytest.raises(ValueError, match="Cannot parse date"):
            fmt_date("not-a-date")


class TestFmtReal:
    def test_integer_value(self):
        assert fmt_real(570, 11) == "00000570.00"

    def test_decimal_value(self):
        assert fmt_real(1.5, 11) == "00000001.50"

    def test_negative_value(self):
        assert fmt_real(-4.0, 11) == "-0000004.00"

    def test_negative_fraction(self):
        assert fmt_real(-0.5, 11) == "-0000000.50"

    def test_zero(self):
        assert fmt_real(0, 11) == "00000000.00"

    def test_large_value(self):
        assert fmt_real(12345.67, 11) == "00012345.67"

    def test_width_15(self):
        assert fmt_real(570.0, 15) == "000000000570.00"
