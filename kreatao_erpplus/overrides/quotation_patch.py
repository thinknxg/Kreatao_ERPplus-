import frappe

def make_customer_from_quotation(source_name, ignore_permissions=False):
    from erpnext.selling.doctype.quotation.quotation import (
        create_customer_from_lead,
        create_customer_from_prospect,
    )
    quotation = frappe.db.get_value(
        "Quotation",
        source_name,
        ["order_type", "quotation_to", "party_name", "customer_name", "custom_customer"],
        as_dict=1,
    )
    if quotation.quotation_to == "Customer":
        return frappe.get_doc("Customer", quotation.party_name)

    existing_customer = None
    if quotation.quotation_to == "Lead":
        existing_customer = frappe.db.get_value("Customer", {"lead_name": quotation.party_name})
        if not existing_customer and quotation.custom_customer:
            existing_customer = quotation.custom_customer
    elif quotation.quotation_to == "Prospect":
        existing_customer = frappe.db.get_value("Customer", {"prospect_name": quotation.party_name})

    if existing_customer:
        return frappe.get_doc("Customer", existing_customer)

    if quotation.quotation_to == "Lead":
        return create_customer_from_lead(quotation.party_name, ignore_permissions=ignore_permissions)
    elif quotation.quotation_to == "Prospect":
        return create_customer_from_prospect(quotation.party_name, ignore_permissions=ignore_permissions)
    return None

@frappe.whitelist()
def create_prospect_from_lead(lead_name, prospect_name):
    lead = frappe.get_doc("Lead", lead_name)
    lead.create_prospect_and_contact({"create_prospect": 1, "prospect_name": prospect_name})
    frappe.db.commit()
    prospects = lead.get_linked_prospects()
    return prospects[-1].parent if prospects else None

@frappe.whitelist()
def make_customer_from_lead(source_name, target_doc=None):
    from erpnext.crm.doctype.lead.lead import _make_customer
    prospect = frappe.db.get_value(
        "Prospect Lead",
        {"lead": source_name},
        "parent"
    )
    doc = _make_customer(source_name, target_doc)
    if prospect:
        doc.prospect_name = prospect
    return doc

@frappe.whitelist()
def make_opportunity_from_lead(source_name, target_doc=None):
    from erpnext.crm.doctype.lead.lead import make_opportunity
    doc = make_opportunity(source_name, target_doc)
    doc.custom_project_title = frappe.db.get_value("Lead", source_name, "custom_project_title")
    doc.custom_project_description = frappe.db.get_value("Lead", source_name, "custom_project_description")
    return doc

@frappe.whitelist()
def make_quotation_from_lead(source_name, target_doc=None):
    from erpnext.crm.doctype.lead.lead import make_quotation
    doc = make_quotation(source_name, target_doc)
    lead = frappe.db.get_value("Lead", source_name, ["custom_project_title", "custom_project_description"], as_dict=1)
    doc.custom_project_title = lead.custom_project_title
    doc.custom_project_description = lead.custom_project_description
    doc.custom_lead = source_name
    # set quotation_to as Prospect or Customer if linked
    prospect = frappe.db.get_value("Prospect Lead", {"lead": source_name}, "parent")
    if prospect:
        customer = frappe.db.get_value("Customer", {"prospect_name": prospect})
        if customer:
            doc.quotation_to = "Customer"
            doc.party_name = customer
        else:
            doc.quotation_to = "Prospect"
            doc.party_name = prospect
    return doc
