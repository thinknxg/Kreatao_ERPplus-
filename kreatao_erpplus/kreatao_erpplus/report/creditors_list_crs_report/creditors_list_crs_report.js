// Copyright (c) 2026, Sandrose and contributors
// For license information, please see license.txt

frappe.query_reports["Creditors List CRS Report"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "report_date",
			label: __("Posting Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "ageing_based_on",
			label: __("Ageing Based On"),
			fieldtype: "Select",
			options: "Posting Date\nDue Date",
			default: "Due Date",
		},
		{
			fieldname: "range",
			label: __("Ageing Range"),
			fieldtype: "Data",
			default: "30, 60, 90, 120",
		},
		{
			fieldname: "finance_book",
			label: __("Finance Book"),
			fieldtype: "Link",
			options: "Finance Book",
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: () => {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						company: company,
					},
				};
			},
		},
		{
			fieldname: "party_type",
			label: __("Party Type"),
			fieldtype: "Autocomplete",
			options: get_party_type_options(),
			on_change: function () {
				frappe.query_report.set_filter_value("party", "");
				frappe.query_report.toggle_filter_display(
					"supplier_group",
					frappe.query_report.get_filter_value("party_type") !== "Supplier"
				);
			},
		},
		{
			fieldname: "party",
			label: __("Party"),
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				if (!frappe.query_report.filters) return;

				let party_type = frappe.query_report.get_filter_value("party_type");
				if (!party_type) return;

				return frappe.db.get_link_options(party_type, txt);
			},
		},
		{
			fieldname: "payment_terms_template",
			label: __("Payment Terms Template"),
			fieldtype: "Link",
			options: "Payment Terms Template",
		},
		{
			fieldname: "supplier_group",
			label: __("Supplier Group"),
			fieldtype: "Link",
			options: "Supplier Group",
		},
		{
			fieldname: "based_on_payment_terms",
			label: __("Based On Payment Terms"),
			fieldtype: "Check",
		},
		{
			fieldname: "for_revaluation_journals",
			label: __("Revaluation Journals"),
			fieldtype: "Check",
		},
	],

	onload: function (report) {
		report.page.add_inner_button(__("Accounts Payable"), function () {
			var filters = report.get_values();
			frappe.set_route("query-report", "Accounts Payable", { company: filters.company });
		});
	},

	// ------------------- Formatter -------------------
    formatter: function (value, row, column, data, default_formatter) {
        // apply default formatting first
        value = default_formatter(value, row, column, data);

        if (!data) return value;

        // Outstanding - Red if > 0
        if (column.fieldname === "outstanding" && data.outstanding > 0) {
            value = `<span style="color:#d9534f; font-weight:bold;">${value}</span>`;
        }

        // PDC 
        if (column.fieldname === "pdc" && data.pdc > 0) {
            value = `<span style="color:#d9534f; font-weight:bold;">${value}</span>`;
        }

        // Total PO
        if (column.fieldname === "total_po_amount" && data.total_po_amount > 0) {
            value = `<span style="color:#d9534f; font-weight:bold;">${value}</span>`;
        }

        // Net CRS - Green if positive, Dark Red if very high
        if (column.fieldname === "net_crs") {
            if (data.net_crs > 0 && data.net_crs < 100000) {
                value = `<span style="color:#d9534f; font-weight:bold;">${value}</span>`;
            } else if (data.net_crs >= 100000) {
                value = `<span style="color:#8b0000; font-weight:bold;">${value}</span>`;
            }
        }

        return value;
    }
};

erpnext.utils.add_dimensions("Accounts Payable Summary", 9);

function get_party_type_options() {
	let options = [];
	frappe.db
		.get_list("Party Type", { filters: { account_type: "Payable" }, fields: ["name"] })
		.then((res) => {
			res.forEach((party_type) => {
				options.push(party_type.name);
			});
		});
	return options;
}





// blue - 0275d8