def execute():
    filepath = '/home/gwm/frappe-bench/apps/erpnext/erpnext/selling/doctype/quotation/quotation.py'
    with open(filepath, 'r') as f:
        content = f.read()
    old = '\t\texisting_customer = frappe.db.get_value("Customer", {"lead_name": quotation.party_name})\n\telif quotation.quotation_to == "Prospect":'
    new = '\t\texisting_customer = frappe.db.get_value("Customer", {"lead_name": quotation.party_name})\n\t\tif not existing_customer:\n\t\t\tcustom_customer = frappe.db.get_value("Quotation", source_name, "custom_customer")\n\t\t\tif custom_customer:\n\t\t\t\texisting_customer = custom_customer\n\telif quotation.quotation_to == "Prospect":'
    if old in content:
        content = content.replace(old, new)
        with open(filepath, 'w') as f:
            f.write(content)
        print("Quotation patch applied")
    else:
        print("Already patched - skipping")
