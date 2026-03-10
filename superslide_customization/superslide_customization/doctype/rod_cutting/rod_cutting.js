// ==========================================================
// ROD CUTTING CALCULATIONS 
// ==========================================================

frappe.ui.form.on("Rod Cutting Pieces", {

    piece_length(frm, cdt, cdn) {
        calculate_piece_total(frm, cdt, cdn);
    },

    qty(frm, cdt, cdn) {
        calculate_piece_total(frm, cdt, cdn);
    }

});

//testing comment

function calculate_piece_total(frm, cdt, cdn) {

    let row = locals[cdt][cdn];

    let piece_length = flt(row.piece_length);
    let qty = flt(row.qty);

    let total = piece_length * qty;

    frappe.model.set_value(cdt, cdn, "total_length", total);

    calculate_output_total(frm);
}

// ==========================================================
// TOTAL OUTPUT LENGTH
// ==========================================================

function calculate_output_total(frm) {

    let total_output = 0;

    (frm.doc.rod_cutting_pieces || []).forEach(row => {
        total_output += flt(row.total_length);
    });

    frm.set_value("total_output_length", total_output);

    calculate_difference(frm);
}



// ==========================================================
// INPUT LENGTH CALCULATION
// ==========================================================

frappe.ui.form.on("ROD Cutting", {

    rod_length(frm) {
        calculate_input_length(frm);
    },

    qty(frm) {
        calculate_input_length(frm);
    },

    refresh(frm) {
        calculate_input_length(frm);
        calculate_output_total(frm);
    }

});


function calculate_input_length(frm) {

    let rod_length = flt(frm.doc.rod_length);
    let qty = flt(frm.doc.qty);

    let total_input = rod_length * qty;

    frm.set_value("total_input_length", total_input);

    calculate_difference(frm);
}


// ==========================================================
// DIFFERENCE
// ==========================================================

function calculate_difference(frm) {

    let input = flt(frm.doc.total_input_length);
    let output = flt(frm.doc.total_output_length);

    let diff = input - output;

    frm.set_value("difference", diff);
}