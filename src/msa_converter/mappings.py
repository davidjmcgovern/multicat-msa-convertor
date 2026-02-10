"""Constants, lookup tables, and column aliases for MSA MultiCat format."""

# CSV column name normalization (handle typos, trailing spaces)
COLUMN_ALIASES = {
    "Catagories": "Categories",
    "on hand Inventory": "OnHandInventory",
    "Invoice 3": "Invoice",
    "Invoice Number": "Invoice",
    "Cash/carry": "CashCarry",
    "Class of trade": "ClassOfTrade",
    "Item Code": "ItemCode",
    "Item Description": "ItemDescription",
    "UPC Code": "UPCCode",
    "Customer Number": "CustomerNumber",
    "Customer Name": "CustomerName",
    "Selling Unit": "SellingUnit",
}

# Category name -> 6-digit MSA Category Code
MSA_CATEGORY_CODES = {
    "Cigarettes": "003231",
    "Cigars": "003251",
    "Cigarillos": "003252",
    "Pipe Tobacco": "003241",
    "Moist Snuff": "003211",
    "Loose Leaf Chewing Tobacco": "003212",
    "Dry Snuff": "003213",
    "Twist/Rope": "003214",
    "SNUS": "003217",
    "Compressed Tobacco": "003218",
    "RYO/MYO Tobacco": "003221",
    "Premium Cigars": "003227",
    "Papers/Tubes/Wraps": "003261",
    "E-Cigarettes": "003292",
    "Tobacco Derived Products": "003293",
}

# Yes/No text -> single-char indicator
YES_NO_MAP = {
    "Yes": "Y",
    "No": "N",
    "yes": "Y",
    "no": "N",
    "Y": "Y",
    "N": "N",
    "": "N",
}
