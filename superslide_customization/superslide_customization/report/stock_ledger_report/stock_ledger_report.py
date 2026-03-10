import frappe


def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


# ---------------------------------------------------------
# COLUMNS
# ---------------------------------------------------------

def get_columns():

    return [

        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120
        },

        {
            "label": "Posting Time",
            "fieldname": "posting_time",
            "fieldtype": "Time",
            "width": 100
        },

        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },

        {
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 200
        },

        {
            "label": "Custom Length",
            "fieldname": "custom_length",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Millimeter",
            "fieldname": "millimeter",
            "fieldtype": "Float",
            "width": 150
        },

        {
            "label": "Warehouse",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 180
        },

        {
            "label": "Actual Qty",
            "fieldname": "actual_qty",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Balance Qty",
            "fieldname": "qty_after_transaction",
            "fieldtype": "Float",
            "width": 140
        },

        {
            "label": "Voucher Type",
            "fieldname": "voucher_type",
            "fieldtype": "Data",
            "width": 150
        },

        {
            "label": "Voucher No",
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 170
        },

        {
            "label": "Company",
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 150
        }

    ]


# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------

def get_data(filters):

    conditions = ""
    values = {}

    if filters.get("company"):
        conditions += " AND sle.company = %(company)s"
        values["company"] = filters.get("company")

    if filters.get("item_code"):
        conditions += " AND sle.item_code = %(item_code)s"
        values["item_code"] = filters.get("item_code")

    if filters.get("warehouse"):
        conditions += " AND sle.warehouse = %(warehouse)s"
        values["warehouse"] = filters.get("warehouse")

    if filters.get("voucher_type"):
        conditions += " AND sle.voucher_type = %(voucher_type)s"
        values["voucher_type"] = filters.get("voucher_type")

    if filters.get("from_date"):
        conditions += " AND sle.posting_date >= %(from_date)s"
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND sle.posting_date <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    data = frappe.db.sql(f"""

        SELECT
            sle.posting_date,
            sle.posting_time,
            sle.item_code,
            item.item_name,
            item.custom_length,

            CASE
                WHEN sle.warehouse LIKE '%%Cut%%'
                THEN item.custom_length / ABS(sle.actual_qty)
                ELSE item.custom_length * ABS(sle.actual_qty)
            END AS millimeter,

            sle.warehouse,
            sle.actual_qty,
            sle.qty_after_transaction,
            sle.voucher_type,
            sle.voucher_no,
            sle.company

        FROM
            `tabStock Ledger Entry` sle

        LEFT JOIN
            `tabItem` item
        ON
            sle.item_code = item.name

        WHERE
            sle.docstatus < 2
            {conditions}

        ORDER BY
            sle.posting_date DESC,
            sle.posting_time DESC

    """, values, as_dict=True)

    return data