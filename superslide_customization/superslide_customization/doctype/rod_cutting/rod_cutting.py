import frappe
from frappe.model.document import Document

class RODCutting(Document):

    def validate(self):

        if not self.item:
            frappe.throw("Item is required")

        if not self.warehouse:
            frappe.throw("Warehouse is required")

        if not self.qty:
            frappe.throw("Quantity is required")

        if not self.rod_cutting_pieces:
            frappe.throw("Add at least one rod cutting piece")

        self.calculate_totals()

        if self.total_input_length <= 0:
            frappe.throw("Invalid input rod length")

        if self.total_output_length <= 0:
            frappe.throw("Output pieces cannot be zero")

        if abs(self.difference) > 0.001:
            frappe.throw(
                f"Input Length ({self.total_input_length}) must equal Output Length ({self.total_output_length})"
            )

    # ==========================================================
    # CALCULATIONS
    # ==========================================================

    def calculate_totals(self):

        self.total_input_length = (self.rod_length or 0) * (self.qty or 0)

        total_output = 0

        for row in self.rod_cutting_pieces:

            if not row.item:
                frappe.throw(f"Item required in row {row.idx}")

            if not row.qty:
                frappe.throw(f"Qty required in row {row.idx}")

            if not row.warehouse:
                frappe.throw(f"Warehouse required in row {row.idx}")

            row.total_length = (row.piece_length or 0) * (row.qty or 0)

            total_output += row.total_length

        self.total_output_length = total_output

        self.difference = self.total_input_length - self.total_output_length

    # ==========================================================
    # ON SUBMIT → CREATE STOCK ENTRY
    # ==========================================================

    def on_submit(self):

        stock_entry = self.create_stock_entry()

        self.db_set("stock_entry_ref", stock_entry.name)

    # ==========================================================
    # CREATE REPACK STOCK ENTRY
    # ==========================================================

    def create_stock_entry(self):

        try:

            se = frappe.new_doc("Stock Entry")

            se.stock_entry_type = "Repack"
            se.company = frappe.defaults.get_user_default("Company")

            # -------------------------------------------------
            # OUT ITEM (Full Rod)
            # -------------------------------------------------

            se.append(
                "items",
                {
                    "item_code": self.item,
                    "qty": self.qty,
                    "s_warehouse": self.warehouse,
                },
            )

            # -------------------------------------------------
            # IN ITEMS (Cut Pieces → Row Warehouse)
            # -------------------------------------------------

            for row in self.rod_cutting_pieces:

                se.append(
                    "items",
                    {
                        "item_code": row.item,
                        "qty": row.qty,
                        "t_warehouse": row.warehouse,
                    },
                )

            # -------------------------------------------------
            # APPLY LENGTH CALCULATION
            # -------------------------------------------------

            for item in se.items:

                if not item.item_code or not item.qty:
                    continue

                length = 0

                # Safe field existence check
                if frappe.db.has_column("Item", "custom_length"):
                    length = frappe.db.get_value("Item", item.item_code, "custom_length") or 0

                length = float(length)

                if item.qty != 0:

                    # If going to cut warehouse
                    if item.t_warehouse and "Cut" in item.t_warehouse:

                        item.custom_millimeter = length / item.qty if length else 0

                    else:

                        item.custom_millimeter = length * item.qty if length else 0
                        
            # -------------------------------------------------
            # INSERT + SUBMIT
            # -------------------------------------------------

            se.insert(ignore_permissions=True)
            se.submit()

            return se

        except Exception:

            frappe.log_error(
                frappe.get_traceback(),
                "Rod Cutting Stock Entry Creation Failed",
            )

            frappe.throw("Failed to create Stock Entry")