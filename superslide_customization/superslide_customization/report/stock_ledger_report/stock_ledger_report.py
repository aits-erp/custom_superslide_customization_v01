import frappe


def execute(filters=None):

    filters = frappe._dict(filters or {})

    columns = get_columns()
    data = get_data(filters)

    total_qty = 0
    total_length = 0

    for row in data:
        total_qty += float(row.get("qty") or 0)
        total_length += float(row.get("total_length") or 0)

    # Grand total row
    total_row = {
        "posting_date": "",
        "posting_time": "",
        "item_code": "",
        "item_name": "<b>Grand Total</b>",
        "length": "",
        "qty": total_qty,
        "total_length": total_length,
        "warehouse": "",
        "balance_qty": "",
        "voucher_type": "",
        "voucher_no": "",
        "company": ""
    }

    data.append(total_row)

    return columns, data


def get_columns():

    return [

        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},

        {"label": "Posting Time", "fieldname": "posting_time", "fieldtype": "Time", "width": 100},

        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},

        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},

        {"label": "Length", "fieldname": "length", "fieldtype": "Float", "width": 120},

        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 100},

        {"label": "Total Length", "fieldname": "total_length", "fieldtype": "Float", "width": 150},

        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 180},

        {"label": "Balance Qty", "fieldname": "balance_qty", "fieldtype": "Float", "width": 120},

        {"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data", "width": 150},

        {"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 170},

        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
    ]


def get_data(filters):

    conditions = []
    values = {}

    if filters.get("ledger_type") == "Full Length Stock Ledger":

        conditions.append("sle.warehouse = 'FL - TTCPL'")
        length_expr = "item.custom_length"
        total_expr = "item.custom_length * sle.actual_qty"

    else:

        conditions.append("sle.warehouse = 'Cut Length - TTCPL'")
        length_expr = "MAX(rcp.piece_length)"
        total_expr = "MAX(rcp.piece_length) * ABS(sle.actual_qty)"

    if filters.get("company"):
        conditions.append("sle.company = %(company)s")
        values["company"] = filters.get("company")

    if filters.get("item_code"):
        conditions.append("sle.item_code = %(item_code)s")
        values["item_code"] = filters.get("item_code")

    if filters.get("warehouse"):
        conditions.append("sle.warehouse = %(warehouse)s")
        values["warehouse"] = filters.get("warehouse")

    if filters.get("from_date"):
        conditions.append("sle.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("sle.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    condition_sql = " AND ".join(conditions)

    if condition_sql:
        condition_sql = "AND " + condition_sql

    query = f"""

        SELECT
            sle.posting_date,
            sle.posting_time,
            sle.item_code,
            item.item_name,

            {length_expr} AS length,

            sle.actual_qty AS qty,

            {total_expr} AS total_length,

            sle.warehouse,
            sle.qty_after_transaction AS balance_qty,
            sle.voucher_type,
            sle.voucher_no,
            sle.company

        FROM
            `tabStock Ledger Entry` sle

        LEFT JOIN
            `tabItem` item
        ON
            sle.item_code = item.name

        LEFT JOIN
            `tabROD Cutting` rc
        ON
            rc.stock_entry_ref = sle.voucher_no

        LEFT JOIN
            `tabRod Cutting Pieces` rcp
        ON
            rcp.parent = rc.name
            AND rcp.item = sle.item_code

        WHERE
            sle.docstatus < 2
            {condition_sql}

        GROUP BY
            sle.name

        ORDER BY
            sle.posting_date DESC,
            sle.posting_time DESC

    """

    return frappe.db.sql(query, values, as_dict=True)