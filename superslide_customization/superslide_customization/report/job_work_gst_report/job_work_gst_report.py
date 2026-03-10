import frappe


def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    data = add_grand_total(data)

    return columns, data


def get_columns():

    return [

        {"label": "SR No", "fieldname": "sr_no", "fieldtype": "Int", "width": 60},

        {"label": "GSTIN of Job Worker", "fieldname": "gstin", "width": 170},

        {"label": "State", "fieldname": "state", "width": 120},

        {"label": "Challan Number", "fieldname": "challan", "width": 180},

        {"label": "Challan Date", "fieldname": "date", "fieldtype": "Date", "width": 120},

        {"label": "Description of Goods", "fieldname": "item_name", "width": 220},

        {"label": "UQC", "fieldname": "uqc", "width": 90},

        {"label": "Quantity", "fieldname": "qty", "fieldtype": "Float", "width": 120},

        {"label": "Taxable Value", "fieldname": "value", "fieldtype": "Currency", "width": 150},

        {"label": "Labour Charge", "fieldname": "labour", "fieldtype": "Currency", "width": 150},

        {"label": "IGST Rate (%)", "fieldname": "igst", "width": 100},

        {"label": "CGST Rate (%)", "fieldname": "cgst", "width": 100},

        {"label": "SGST Rate (%)", "fieldname": "sgst", "width": 100},

    ]


def get_data(filters):

    conditions = ""

    if filters.get("supplier"):
        conditions += " AND sup.name = %(supplier)s"

    if filters.get("item_code"):
        conditions += " AND item.item_code = %(item_code)s"


    # ---------------------------------
    # TO JOB WORK
    # ---------------------------------

    if filters.get("report_type") == "To Job Work":

        query = """

        SELECT

            se.name as challan,
            se.posting_date as date,
            sed.item_name,
            sed.qty,
            sed.uom,
            sup.gstin,
            addr.state,
            sed.amount as value

        FROM `tabStock Entry` se

        JOIN `tabStock Entry Detail` sed
            ON sed.parent = se.name

        LEFT JOIN `tabSupplier` sup
            ON sup.name = se.supplier

        LEFT JOIN `tabAddress` addr
            ON addr.name = sup.supplier_primary_address

        LEFT JOIN `tabItem` item
            ON item.name = sed.item_code

        WHERE
            se.docstatus = 1
            AND se.stock_entry_type = 'Material Transfer to Supplier'
            AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s

        """ + conditions


    # ---------------------------------
    # FROM JOB WORK
    # ---------------------------------

    else:

        query = """

        SELECT

            sr.name as challan,
            sr.posting_date as date,
            sri.item_name,
            sri.qty,
            sri.uom,
            sup.gstin,
            addr.state,
            sri.amount as value

        FROM `tabSubcontracting Receipt` sr

        JOIN `tabSubcontracting Receipt Item` sri
            ON sri.parent = sr.name

        LEFT JOIN `tabSupplier` sup
            ON sup.name = sr.supplier

        LEFT JOIN `tabAddress` addr
            ON addr.name = sup.supplier_primary_address

        LEFT JOIN `tabItem` item
            ON item.name = sri.item_code

        WHERE
            sr.docstatus = 1
            AND sr.posting_date BETWEEN %(from_date)s AND %(to_date)s

        """ + conditions


    records = frappe.db.sql(query, filters, as_dict=1)

    data = []

    for i, d in enumerate(records, start=1):

        data.append({

            "sr_no": i,
            "gstin": d.gstin,
            "state": d.state,
            "challan": d.challan,
            "date": d.date,
            "item_name": d.item_name,
            "uqc": get_uqc(d.uom),
            "qty": d.qty,
            "value": d.value,
            "labour": 0,
            "igst": 0,
            "cgst": 0,
            "sgst": 0

        })

    return data


# -------------------------
# UQC Mapping
# -------------------------

def get_uqc(uom):

    mapping = {

        "Nos": "NOS",
        "Kg": "KGS",
        "Gram": "GMS",
        "Litre": "LTR",
        "Meter": "MTR"

    }

    return mapping.get(uom, uom)


# -------------------------
# Grand Total
# -------------------------

def add_grand_total(data):

    total_qty = 0
    total_value = 0

    for row in data:

        total_qty += row["qty"]
        total_value += row["value"]

    data.append({

        "item_name": "GRAND TOTAL",
        "qty": total_qty,
        "value": total_value

    })

    return data