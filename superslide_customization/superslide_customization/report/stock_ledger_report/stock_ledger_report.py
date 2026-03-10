import frappe


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [

        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": "Posting Time", "fieldname": "posting_time", "fieldtype": "Time", "width": 90},

        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},

        {"label": "Length", "fieldname": "length", "fieldtype": "Float", "width": 120},

        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 100},

        {"label": "Total Length", "fieldname": "total_length", "fieldtype": "Float", "width": 160},

        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 180},

        {"label": "Balance Qty", "fieldname": "balance_qty", "fieldtype": "Float", "width": 120},

        {"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data", "width": 140},

        {"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 160},

        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
    ]


def get_data(filters):

    conditions = []
    values = {}

    # -----------------------------------------------------
    # Ledger Type Logic
    # -----------------------------------------------------

    if filters.ledger_type == "Full Length Stock Ledger":
        conditions.append("sle.warehouse = 'FL - TTCPL'")
        length_expr = "item.custom_length"
        total_expr = "item.custom_length * sle.actual_qty"

    else:
        conditions.append("sle.warehouse = 'Cut Length - TTCPL'")
        length_expr = "MAX(rcp.piece_length)"
        total_expr = "MAX(rcp.piece_length) * ABS(sle.actual_qty)"

    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------

    if filters.company:
        conditions.append("sle.company = %(company)s")
        values["company"] = filters.company

    if filters.item_code:
        conditions.append("sle.item_code = %(item_code)s")
        values["item_code"] = filters.item_code

    if filters.warehouse:
        conditions.append("sle.warehouse = %(warehouse)s")
        values["warehouse"] = filters.warehouse

    if filters.from_date:
        conditions.append("sle.posting_date >= %(from_date)s")
        values["from_date"] = filters.from_date

    if filters.to_date:
        conditions.append("sle.posting_date <= %(to_date)s")
        values["to_date"] = filters.to_date

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