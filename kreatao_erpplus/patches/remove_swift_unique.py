import frappe

def execute():
    indexes = frappe.db.sql("""
        SHOW INDEX FROM `tabBank` WHERE Key_name='swift_number' AND Non_unique=0
    """)
    if indexes:
        frappe.db.sql("ALTER TABLE `tabBank` DROP INDEX swift_number")
