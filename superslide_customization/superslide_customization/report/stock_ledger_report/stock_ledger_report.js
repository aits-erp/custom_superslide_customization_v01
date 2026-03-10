frappe.query_reports["Stock Ledger Report"] = {

    "filters": [

        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1
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
            "fieldname": "voucher_type",
            "label": "Voucher Type",
            "fieldtype": "Select",
            "options": "\nStock Entry\nPurchase Receipt\nDelivery Note\nStock Reconciliation"
        }

    ]

};