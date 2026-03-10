frappe.query_reports["Combined Stock Ledger"] = {

    "filters": [

        {
            "fieldname": "ledger_type",
            "label": "Ledger Type",
            "fieldtype": "Select",
            "options": [
                "Full Length Stock Ledger",
                "Cut Piece Stock Ledger"
            ],
            "default": "Full Length Stock Ledger",
            "reqd": 1
        },

        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company"
        },

        {
            "fieldname": "item_code",
            "label": "Item",
            "fieldtype": "Link",
            "options": "Item"
        },

        {
            "fieldname": "warehouse",
            "label": "Warehouse",
            "fieldtype": "Link",
            "options": "Warehouse"
        },

        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date"
        },

        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date"
        }

    ]

};