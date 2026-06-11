app_name = "kreatao_erpplus"
app_title = "KREATAO ERP +"
app_publisher = "krishna"
app_description = "ERP EXtensions"
app_email = "kpriyapv20@gmail.com"
app_license = "mit"
doctype_js = {
    "Payment Entry": "public/js/payment_entry.js",
}
process_soa_html = {
    "General Ledger": ["kreatao_erpplus/templates/process_statement_of_accounts.html"],
    "Accounts Receivable": ["kreatao_erpplus/templates/process_statement_of_accounts_accounts_receivable.html"],
}
override_doctype_class = {
    "Quotation": "kreatao_erpplus.quotation_naming.CustomQuotation"
}
override_doctype_dashboards = {
    "Lead": "kreatao_erpplus.overrides.lead_dashboard.get_data",
    "Customer": "kreatao_erpplus.overrides.customer_dashboard.get_data",
}
override_whitelisted_methods = {
    "erpnext.selling.doctype.quotation.quotation._make_customer": "kreatao_erpplus.overrides.quotation_patch.make_customer_from_quotation",
}
after_migrate = [
    "kreatao_erpplus.patches.fix_quotation_make_customer.execute",
    "kreatao_erpplus.patches.remove_swift_unique.execute"
]
fixtures = [
    {"dt": "Client Script", "filters": [["name", "in", [
        "Lead-Prospect-Buttons",
        "Quotation-Customer-Autofill",
        "Lead-View-Customer",
        "GWM Quotation Naming Series Fix"
    ]]]},
    {"dt": "Server Script", "filters": [["name", "in", [
        "GWM Quotation Cancel Rev",
        "GWM Quotation Auto Name",
        "save_item_prices",
        "fetch_item_prices"
    ]]]},
    {"dt": "Custom Field", "filters": [["dt", "in", [
        "Lead", "Opportunity", "Project", "Project Milestone",
        "Quotation", "Customer", "CRM Deal"
    ]]]}
]
