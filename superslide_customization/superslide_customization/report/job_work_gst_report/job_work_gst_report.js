frappe.query_reports["Job Work GST Report"] = {

    filters: [

        {
            fieldname: "report_type",
            label: "Report Type",
            fieldtype: "Select",
            options: ["To Job Work", "From Job Work"],
            default: "To Job Work",
            reqd: 1
        },

        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            reqd: 1
        },

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1
        },

        {
            fieldname: "supplier",
            label: "Job Worker",
            fieldtype: "Link",
            options: "Supplier"
        },

        {
            fieldname: "item_code",
            label: "Item",
            fieldtype: "Link",
            options: "Item"
        }

    ]
};