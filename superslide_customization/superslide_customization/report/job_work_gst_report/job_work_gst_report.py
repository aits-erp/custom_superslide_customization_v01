import frappe


def execute(filters=None):

    columns = get_columns()

    if filters.get("report_type") == "From Job Work":
        data = get_from_job_work(filters)
    else:
        data = get_to_job_work(filters)

    data = add_total_row(data)

    return columns, data


# -----------------------------
# Columns
# -----------------------------

def get_columns():

    return [

        {"label": "SR No", "fieldname": "sr_no", "width": 70},

        {"label": "GSTIN of Job Worker", "fieldname": "gstin", "width": 180},

        {"label": "State", "fieldname": "state", "width": 120},

        {"label": "Challan Number", "fieldname": "challan", "width": 180},

        {"label": "Challan Date", "fieldname": "date", "fieldtype": "Date", "width": 120},

        {"label": "Item Code", "fieldname": "item_code", "width": 140},

        {"label": "Description of Goods", "fieldname": "item_name", "width": 200},

        {"label": "UQC", "fieldname": "uqc", "width": 100},

        {"label": "Quantity", "fieldname": "qty", "fieldtype": "Float", "width": 120},

        {"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": 120},

        {"label": "Taxable Value", "fieldname": "taxable_value", "fieldtype": "Currency", "width": 150},

        {"label": "Labour Charge", "fieldname": "labour", "fieldtype": "Currency", "width": 130},

        {"label": "CGST %", "fieldname": "cgst", "width": 80},

        {"label": "SGST %", "fieldname": "sgst", "width": 80},

        {"label": "IGST %", "fieldname": "igst", "width": 80}

    ]


# -----------------------------
# FROM JOB WORK
# -----------------------------

def get_from_job_work(filters):

    conditions = ""

    if filters.get("supplier"):
        conditions += " AND sr.supplier = %(supplier)s"

    if filters.get("item_code"):
        conditions += " AND sri.item_code = %(item_code)s"

    query = f"""

        SELECT
            sr.name AS challan,
            sr.posting_date AS date,
            sr.supplier,
            sri.item_code,
            sri.item_name,
            sri.stock_uom AS uqc,
            sri.qty,
            sri.rate,
            (sri.qty * sri.rate) AS taxable_value

        FROM `tabSubcontracting Receipt` sr

        JOIN `tabSubcontracting Receipt Item` sri
            ON sri.parent = sr.name

        WHERE
            sr.docstatus = 1
            AND sr.company = %(company)s
            AND sr.posting_date BETWEEN %(from_date)s AND %(to_date)s
            {conditions}

        ORDER BY sr.posting_date DESC

    """

    records = frappe.db.sql(query, filters, as_dict=True)

    return enrich_supplier_data(records)


# -----------------------------
# TO JOB WORK
# -----------------------------

def get_to_job_work(filters):

    conditions = ""

    if filters.get("supplier"):
        conditions += " AND se.supplier = %(supplier)s"

    if filters.get("item_code"):
        conditions += " AND sed.item_code = %(item_code)s"

    query = f"""

        SELECT
            se.name AS challan,
            se.posting_date AS date,
            se.supplier,
            sed.item_code,
            sed.item_name,
            sed.uom AS uqc,
            sed.qty,
            sed.valuation_rate AS rate,
            (sed.qty * sed.valuation_rate) AS taxable_value

        FROM `tabStock Entry` se

        JOIN `tabStock Entry Detail` sed
            ON sed.parent = se.name

        WHERE
            se.docstatus = 1
            AND se.company = %(company)s
            AND se.supplier IS NOT NULL
            AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s
            {conditions}

        ORDER BY se.posting_date DESC

    """

    records = frappe.db.sql(query, filters, as_dict=True)

    return enrich_supplier_data(records)


# -----------------------------
# Supplier GSTIN + State
# -----------------------------

def enrich_supplier_data(records):

    data = []

    for i, r in enumerate(records, start=1):

        supplier = frappe.db.get_value(
            "Supplier",
            r.supplier,
            ["gstin", "supplier_primary_address"],
            as_dict=True
        )

        state = ""

        if supplier and supplier.supplier_primary_address:

            state = frappe.db.get_value(
                "Address",
                supplier.supplier_primary_address,
                "state"
            )

        data.append({

            "sr_no": i,
            "gstin": supplier.gstin if supplier else "",
            "state": state,
            "challan": r.challan,
            "date": r.date,
            "item_code": r.item_code,
            "item_name": r.item_name,
            "uqc": map_uqc(r.uqc),
            "qty": r.qty,
            "rate": r.rate,
            "taxable_value": r.taxable_value,
            "labour": 0,
            "cgst": 0,
            "sgst": 0,
            "igst": 0

        })

    return data


# -----------------------------
# GST UQC Mapping
# -----------------------------

def map_uqc(uom):

    mapping = {
        "Nos": "NOS",
        "Kg": "KGS",
        "Gram": "GMS",
        "Litre": "LTR",
        "Meter": "MTR"
    }

    return mapping.get(uom, uom)


# -----------------------------
# GRAND TOTAL
# -----------------------------

def add_total_row(data):

    total_qty = 0
    total_value = 0

    for row in data:

        total_qty += row.get("qty", 0)
        total_value += row.get("taxable_value", 0)

    data.append({

        "item_name": "GRAND TOTAL",
        "qty": total_qty,
        "taxable_value": total_value

    })

    return data