"""Record type definitions for MSA MultiCat Tobacco format.

Each record maps to exact column positions per the MSA spec.
Column positions are 1-indexed in the spec; field order in to_line()
produces the correct layout.
"""

from dataclasses import dataclass, field

from msa_converter.formatter import fmt, fmt_date, fmt_real


@dataclass
class HIDRecord:
    """Header Identification Record (1 per file)."""

    distributor_id: str = ""          # 4-11 (8) Alphanumeric, Full
    project_id: str = "TOB"           # 12-15 (4) Alphanumeric Literal, LJ/BF
    test_flag: str = "T"              # 16 (1) T=Test, blank=Live
    time_interval: str = "W"          # 17 (1) W=Week
    end_date: str = ""                # 18-25 (8) YYYYMMDD
    distributor_name: str = ""        # 26-57 (32) LJ/BF
    distributor_address: str = ""     # 58-147 (90) LJ/BF
    distributor_city: str = ""        # 148-172 (25) LJ/BF
    distributor_state: str = ""       # 173-174 (2) Full
    distributor_zip: str = ""         # 175-183 (9) LJ/BF
    distributor_country: str = ""     # 184-186 (3) LJ/BF
    contact_last_name: str = ""       # 187-206 (20) LJ/BF
    contact_first_name: str = ""      # 207-226 (20) LJ/BF
    contact_phone: str = ""           # 232-241 (10) Numeric, Full
    contact_fax: str = ""             # 247-256 (10) Numeric, Full
    contact_email: str = ""           # 257-316 (60) LJ/BF
    pur_measure_count: str = "0001"   # 325-328 (4) 0001 or 0002
    creation_date: str = ""           # 329-336 (8) YYYYMMDD
    inv_resubmission: str = ""        # 337 (1) 1=resubmit, blank=no

    def to_line(self) -> str:
        return (
            fmt("HID", 3)                                  # 1-3
            + fmt(self.distributor_id, 8)                   # 4-11
            + fmt(self.project_id, 4, justify="L")         # 12-15
            + fmt(self.test_flag, 1)                        # 16
            + fmt(self.time_interval, 1)                    # 17
            + fmt(self.end_date, 8)                         # 18-25
            + fmt(self.distributor_name, 32)                # 26-57
            + fmt(self.distributor_address, 90)             # 58-147
            + fmt(self.distributor_city, 25)                # 148-172
            + fmt(self.distributor_state, 2)                # 173-174
            + fmt(self.distributor_zip, 9)                  # 175-183
            + fmt(self.distributor_country, 3)              # 184-186
            + fmt(self.contact_last_name, 20)               # 187-206
            + fmt(self.contact_first_name, 20)              # 207-226
            + fmt("", 5)                                    # 227-231 dialing code reserved
            + fmt(self.contact_phone, 10)                          # 232-241
            + fmt("", 5)                                    # 242-246 dialing code reserved
            + fmt(self.contact_fax, 10)                            # 247-256
            + fmt(self.contact_email, 60)                   # 257-316
            + fmt("0001", 4, justify="R", fill="0")         # 317-320 BID measures
            + fmt("0000", 4, justify="R", fill="0")         # 321-324 SID measures
            + fmt(self.pur_measure_count, 4, justify="R", fill="0")  # 325-328
            + fmt(self.creation_date, 8)                    # 329-336
            + fmt(self.inv_resubmission, 1)                 # 337
        )


@dataclass
class BIDRecord:
    """Brand Identification Record (1 per unique SKU)."""

    upc: str = ""                     # 4-17 (14) RJ/BF
    sku: str = ""                     # 18-31 (14) RJ/ZF
    product_description: str = ""     # 32-81 (50) LJ/BF
    promotion_description: str = ""   # 82-131 (50) LJ/BF
    items_per_selling_unit: str = ""  # 132-137 (6) RJ/ZF
    promotion_indicator: str = "N"    # 138 (1)
    nacs_category_code: str = ""      # 139-144 (6) Optional, RJ/ZF
    msa_category_code: str = ""       # 145-150 (6) Numeric Literal, Full
    unit_size: str = ""               # 161-166 (6) Optional, RJ/ZF
    unit_size_description: str = ""   # 167-176 (10) Optional, LJ/BF
    shipper_flag: str = ""            # 177 (1)
    mfr_promo_code: str = ""          # 178-187 (10) LJ/BF
    mfr_product_id: str = ""          # 188-201 (14) Optional, LJ/BF
    state_tax_jurisdiction: str = ""  # 208-209 (2)
    inventory: float = 0.0            # 251-261 (11) Real number, RJ/ZF

    def to_line(self) -> str:
        return (
            fmt("BID", 3)                                          # 1-3
            + fmt(self.upc, 14, justify="R")                       # 4-17
            + fmt(self.sku, 14, justify="R", fill="0")             # 18-31
            + fmt(self.product_description, 50)                    # 32-81
            + fmt(self.promotion_description, 50)                  # 82-131
            + fmt(self.items_per_selling_unit, 6, justify="R", fill="0")  # 132-137
            + fmt(self.promotion_indicator, 1)                     # 138
            + fmt(self.nacs_category_code, 6)                          # 139-144
            + fmt(self.msa_category_code, 6)                       # 145-150
            + fmt("", 10)                                          # 151-160 project id reserved
            + fmt(self.unit_size, 6, justify="R", fill="0")        # 161-166
            + fmt(self.unit_size_description, 10)                  # 167-176
            + fmt(self.shipper_flag, 1)                            # 177
            + fmt(self.mfr_promo_code, 10)                         # 178-187
            + fmt(self.mfr_product_id, 14)                         # 188-201
            + fmt("", 2)                                           # 202-203 UPC extension
            + fmt("", 4)                                           # 204-207 UPC year/issue
            + fmt(self.state_tax_jurisdiction, 2)                  # 208-209
            + fmt("", 16, justify="R")                             # 210-225 alt UPC 1
            + fmt("", 16, justify="R")                             # 226-241 alt UPC 2
            + fmt("", 2, justify="R", fill="0")                    # 242-243 spiral size
            + fmt("", 4)                                           # 244-247 reserved
            + fmt("003", 3)                                        # 248-250 measure code 1
            + fmt_real(self.inventory, 11)                         # 251-261 measure value 1
        )


@dataclass
class SIDRecord:
    """Ship-To Identification Record (1 per unique customer location)."""

    customer_number: str = ""            # 4-11 (8) LJ/BF
    shipping_number: str = ""            # 12-19 (8) LJ/BF
    shipping_number_ext: str = ""        # 20-27 (8) Optional, LJ/BF
    customer_name: str = ""              # 28-59 (32) LJ/BF
    store_number: str = ""               # 60-67 (8) Optional, LJ/BF
    address: str = ""                    # 68-157 (90) LJ/BF
    city: str = ""                       # 158-182 (25) LJ/BF
    state: str = ""                      # 183-184 (2)
    zip_code: str = ""                   # 185-193 (9) LJ/BF
    country: str = ""                    # 194-196 (3)
    state_tax_jurisdiction: str = ""     # 197-198 (2)
    phone: str = ""                      # 202-211 (10)
    class_of_trade: str = ""             # 212-231 (20) LJ/BF
    tdlinx_number: str = ""              # 232-238 (7)
    cash_carry_indicator: str = "N"      # 239 (1)
    promo_acceptance: str = ""           # 498 (1)

    def to_line(self) -> str:
        return (
            fmt("SID", 3)                                      # 1-3
            + fmt(self.customer_number, 8)                      # 4-11
            + fmt(self.shipping_number, 8)                      # 12-19
            + fmt(self.shipping_number_ext, 8)                  # 20-27
            + fmt(self.customer_name, 32)                       # 28-59
            + fmt(self.store_number, 8)                         # 60-67
            + fmt(self.address, 90)                             # 68-157
            + fmt(self.city, 25)                                # 158-182
            + fmt(self.state, 2)                                # 183-184
            + fmt(self.zip_code, 9)                             # 185-193
            + fmt(self.country, 3)                              # 194-196
            + fmt(self.state_tax_jurisdiction, 2)               # 197-198
            + fmt("", 3)                                        # 199-201 reserved
            + fmt(self.phone, 10)                                # 202-211
            + fmt(self.class_of_trade, 20)                      # 212-231
            + fmt(self.tdlinx_number, 7)                         # 232-238
            + fmt(self.cash_carry_indicator, 1)                 # 239
            + fmt("", 16)                                       # 240-255 location number
            + fmt("", 2)                                        # 256-257 machine type
            + fmt("", 1)                                        # 258 reserved
            + fmt("", 24)                                       # 259-282 bill to cust number
            + fmt("", 24)                                       # 283-306 bill to group number
            + fmt("", 32)                                       # 307-338 bill to name
            + fmt("", 90)                                       # 339-428 bill to address
            + fmt("", 25)                                       # 429-453 bill to city
            + fmt("", 2)                                        # 454-455 bill to state
            + fmt("", 9)                                        # 456-464 bill to zip
            + fmt("", 3)                                        # 465-467 bill to country
            + fmt("", 5)                                        # 468-472 reserved
            + fmt("", 10, justify="R", fill="0")                # 473-482 bill to phone
            + fmt("", 5, justify="R", fill="0")                 # 483-487 sq feet
            + fmt("", 5, justify="R", fill="0")                 # 488-492 linear feet
            + fmt("", 5, justify="R", fill="0")                 # 493-497 running feet
            + fmt(self.promo_acceptance, 1)                     # 498
            + fmt("", 10)                                       # 499-508 sales rep ID
            + fmt("", 29)                                       # 509-537 reserved
            + fmt("", 3)                                        # 538-540 measure code 1
            + fmt("", 11, justify="R", fill="0")                # 541-551 measure value 1
        )


@dataclass
class PURRecord:
    """Purchase Record (1 per SKU per customer location)."""

    customer_number: str = ""        # 4-11 (8) LJ/BF
    shipping_number: str = ""        # 12-19 (8) LJ/BF
    shipping_number_ext: str = ""    # 20-27 (8) Optional, LJ/BF
    sku: str = ""                    # 28-41 (14) RJ/ZF
    invoice_number: str = ""         # 45-74 (30) Optional, LJ/BF
    transaction_date: str = ""       # 75-82 (8) Optional, YYYYMMDD
    quantity: float = 0.0            # 106-116 (11) Real number, RJ/ZF
    dollars: float | None = None     # 120-130 (11) Optional, Real number, RJ/BF

    def to_line(self) -> str:
        # Include measure code 2 / value 2 only if dollars is provided
        has_dollars = self.dollars is not None
        return (
            fmt("PUR", 3)                                       # 1-3
            + fmt(self.customer_number, 8)                       # 4-11
            + fmt(self.shipping_number, 8)                       # 12-19
            + fmt(self.shipping_number_ext, 8)                   # 20-27
            + fmt(self.sku, 14, justify="R", fill="0")           # 28-41
            + fmt("", 3)                                         # 42-44 reserved
            + fmt(self.invoice_number, 30)                       # 45-74
            + fmt(self.transaction_date, 8)                      # 75-82
            + fmt("", 20)                                        # 83-102 reserved
            + fmt("001", 3)                                      # 103-105 measure code 1
            + fmt_real(self.quantity, 11)                         # 106-116 measure value 1
            + (fmt("002", 3) if has_dollars else fmt("", 3))     # 117-119 measure code 2
            + (fmt_real(self.dollars, 11) if has_dollars
               else fmt("", 11))                                 # 120-130 measure value 2
        )


@dataclass
class TOTRecord:
    """Total Record (1 per file, control totals for validation)."""

    distributor_id: str = ""         # 4-11 (8)
    end_date: str = ""               # 12-19 (8) YYYYMMDD
    bid_count: int = 0               # 20-28 (9) RJ/ZF
    sid_count: int = 0               # 29-37 (9) RJ/ZF
    pur_count: int = 0               # 38-46 (9) RJ/ZF
    total_quantity: float = 0.0      # 90-104 (15) Real number, RJ/ZF
    total_dollars: float | None = None  # 108-122 (15) Optional, Real number, RJ/BF
    total_inventory: float = 0.0     # 126-140 (15) Real number, RJ/ZF

    def to_line(self) -> str:
        has_dollars = self.total_dollars is not None
        return (
            fmt("TOT", 3)                                        # 1-3
            + fmt(self.distributor_id, 8)                         # 4-11
            + fmt(self.end_date, 8)                               # 12-19
            + fmt(str(self.bid_count), 9, justify="R", fill="0")  # 20-28
            + fmt(str(self.sid_count), 9, justify="R", fill="0")  # 29-37
            + fmt(str(self.pur_count), 9, justify="R", fill="0")  # 38-46
            + fmt("", 40)                                         # 47-86 reserved
            + fmt("001", 3)                                       # 87-89 measure code 1
            + fmt_real(self.total_quantity, 15)                    # 90-104 measure value 1
            + (fmt("002", 3) if has_dollars else fmt("", 3))      # 105-107 measure code 2
            + (fmt_real(self.total_dollars, 15) if has_dollars
               else fmt("", 15))                                  # 108-122 measure value 2
            + fmt("003", 3)                                       # 123-125 measure code 3
            + fmt_real(self.total_inventory, 15)                   # 126-140 measure value 3
        )
