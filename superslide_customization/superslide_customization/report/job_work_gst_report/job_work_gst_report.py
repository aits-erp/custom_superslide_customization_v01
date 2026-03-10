import frappe


def execute(filters=None):

    columns = get_columns(filters)
    data = get_data(filters)

    add_grand_total(data)

    return columns, data


# -----------------------------
# Columns
# -----------------------------

def get_columns(filters):

    return [

        {"label": "SR No", "fieldname": "sr_no", "fieldtype": "Int", "width": 70},

        {"label": "GSTIN of Job Worker", "fieldname": "gstin", "width": 170},

        {"label": "State", "fieldname": "state", "width": 120},

        {"label": "Challan Number", "fieldname": "challan", "width": 170},

        {"label": "Challan Date", "fieldname": "date", "fieldtype": "Date", "width": 120},

        {"label": "Description of Goods", "fieldname": "item_name", "width": 220},

        {"label": "UQC", "fieldname": "uqc", "width": 100},

        {"label": "Quantity", "fieldname": "qty", "fieldtype": "Float", "width": 120},

        {"label": "Taxable Value", "fieldname": "value", "fieldtype": "Currency", "width": 150},

        {"label": "Labour Charge", "fieldname": "labour", "fieldtype": "Currency", "width": 150},

        {"label": "IGST Rate %", "fieldname": "igst", "width": 100},

        {"label": "CGST Rate %", "fieldname": "cgst", "width": 100},

        {"label": "SGST Rate %", "fieldname": "sgst", "width": 100},

    ]


# -----------------------------
# Data
# -----------------------------

def get_data(filters):

    conditions = ""

    if filters.from_date:
        conditions += f" AND se.posting_date >= '{filters.from_date}'"

    if filters.to_date:
        conditions += f" AND se.posting_date <= '{filters.to_date}'"

    if filters.supplier:
        conditions += f" AND se.supplier = '{filters.supplier}'"

    if filters.item_code:
        conditions += f" AND sed.item_code = '{filters.item_code}'"


    if filters.report_type == "To Job Work":

        stock_type = "Material Transfer"


    else:

        stock_type = "Subcontract"


    data = frappe.db.sql(f"""

        SELECT

            sup.gstin,
            addr.state,
            se.name as challan,
            se.posting_date as date,
            sed.item_name,
            sed.uom,
            sed.qty,
            sed.amount as value,
            0 as labour

        FROM `tabStock Entry` se

        JOIN `tabStock Entry Detail` sed
            ON sed.parent = se.name

        LEFT JOIN `tabSupplier` sup
            ON sup.name = se.supplier

        LEFT JOIN `tabAddress` addr
            ON addr.name = sup.supplier_primary_address

        WHERE
            se.docstatus = 1
            AND se.stock_entry_type = '{stock_type}'
            {conditions}

    """, as_dict=1)


    result = []

    for i, d in enumerate(data, start=1):

        result.append({

            "sr_no": i,
            "gstin": d.gstin,
            "state": d.state,
            "challan": d.challan,
            "date": d.date,
            "item_name": d.item_name,
            "uqc": get_uqc(d.uom),
            "qty": d.qty,
            "value": d.value,
            "labour": d.labour,
            "igst": get_tax_rate("IGST"),
            "cgst": get_tax_rate("CGST"),
            "sgst": get_tax_rate("SGST")

        })

    return result


# -----------------------------
# UQC Mapping
# -----------------------------

def get_uqc(uom):

    mapping = {

        "Nos": "NOS",
        "Kg": "KGS",
        "Gram": "GMS",
        "Litre": "LTR",
        "Meter": "MTR"

    }

    return mapping.get(uom, uom)


# -----------------------------
# GST Rate Pull
# -----------------------------

def get_tax_rate(tax_type):

    rate = frappe.db.sql("""

        SELECT rate
        FROM `tabItem Tax`
        WHERE tax_type LIKE %s
        LIMIT 1

    """, f"%{tax_type}%", as_dict=1)

    return rate[0].rate if rate else 0


# -----------------------------
# Grand Total
# -----------------------------

def add_grand_total(data):

    total_qty = 0
    total_value = 0

    for d in data:

        total_qty += d["qty"]
        total_value += d["value"]

    data.append({

        "item_name": "GRAND TOTAL",
        "qty": total_qty,
        "value": total_value

    })