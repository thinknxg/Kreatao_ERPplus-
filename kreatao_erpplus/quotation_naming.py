import frappe
from frappe.model.naming import set_name_by_naming_series
from erpnext.selling.doctype.quotation.quotation import Quotation

class CustomQuotation(Quotation):
    def autoname(self):
        prefix = frappe.db.get_value("Company", self.company, "abbr") or "GWM"
        parts = str(self.transaction_date).split("-")
        date_part = parts[2] + parts[1] + parts[0][2:]

        lead_id = None
        if self.quotation_to == "Lead" and self.party_name:
            lead_id = self.party_name
        elif self.quotation_to == "Customer" and self.custom_lead:
            lead_id = self.custom_lead
        elif self.quotation_to == "Prospect" and self.party_name:
            lead_id = frappe.db.get_value("Prospect Lead", {"parent": self.party_name}, "lead") or None

        if lead_id:
            if self.amended_from:
                original = str(self.amended_from)
                if "-Rev " in original:
                    base = original.split("-Rev ")[0]
                    current_rev = int(original.split("-Rev ")[1].split("-")[0])
                else:
                    base = original
                    current_rev = 0
                segments = base.split("-")
                lead_serial = segments[2]
                self.name = prefix + "-" + lead_id + "-" + lead_serial + "-" + date_part + "-Rev " + str(current_rev + 1)
            else:
                count = frappe.db.count("Quotation", filters={
                    "quotation_to": "Lead",
                    "party_name": lead_id,
                })
                serial_num = count + 1
                lead_serial = "L" + str(serial_num).zfill(3)
                self.name = prefix + "-" + lead_id + "-" + lead_serial + "-" + date_part + "-Rev 0"
        else:
            if self.amended_from:
                original = str(self.amended_from)
                if "-Rev " in original:
                    base = original.split("-Rev ")[0]
                    current_rev = int(original.split("-Rev ")[1].split("-")[0])
                else:
                    base = original
                    current_rev = 0
                self.name = base + "-Rev " + str(current_rev + 1)
            else:
                count = frappe.db.count("Quotation", filters={
                    "name": ["like", prefix + "-QTN-%"]
                })
                serial_num = count + 1
                qtn_serial = str(serial_num).zfill(3)
                self.name = prefix + "-QTN-" + qtn_serial + "-" + date_part + "-Rev 0"
