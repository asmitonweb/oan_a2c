import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    # 1. Create A2C Region DocType
    if not frappe.db.exists("DocType", "A2C Region"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "A2C Region",
            "module": "OpenAgriNet Access to Credit",
            "custom": 0,
            "autoname": "field:region_name",
            "fields": [
                {
                    "fieldname": "region_name",
                    "fieldtype": "Data",
                    "label": "Region Name",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1
                }
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "A2C Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "A2C Development Agent", "read": 1},
                {"role": "A2C Bank Agent", "read": 1},
                {"role": "A2C Bank Admin", "read": 1},
            ],
            "naming_rule": "By fieldname",
            "autoname_field": "region_name"
        })
        doc.insert(ignore_permissions=True)
        print("Created A2C Region DocType")

    # 2. Create A2C Woreda DocType
    if not frappe.db.exists("DocType", "A2C Woreda"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "A2C Woreda",
            "module": "OpenAgriNet Access to Credit",
            "custom": 0,
            "autoname": "format:{region}-{woreda_name}",
            "fields": [
                {
                    "fieldname": "woreda_name",
                    "fieldtype": "Data",
                    "label": "Woreda Name",
                    "reqd": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1
                },
                {
                    "fieldname": "region",
                    "fieldtype": "Link",
                    "options": "A2C Region",
                    "label": "Region",
                    "reqd": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1
                }
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "A2C Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "A2C Development Agent", "read": 1},
                {"role": "A2C Bank Agent", "read": 1},
                {"role": "A2C Bank Admin", "read": 1},
            ],
            "naming_rule": "Expression"
        })
        doc.insert(ignore_permissions=True)
        print("Created A2C Woreda DocType")

    # 3. Create A2C Kebele DocType
    if not frappe.db.exists("DocType", "A2C Kebele"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "A2C Kebele",
            "module": "OpenAgriNet Access to Credit",
            "custom": 0,
            "autoname": "format:{woreda}-{kebele_name}",
            "fields": [
                {
                    "fieldname": "kebele_name",
                    "fieldtype": "Data",
                    "label": "Kebele Name",
                    "reqd": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1
                },
                {
                    "fieldname": "woreda",
                    "fieldtype": "Link",
                    "options": "A2C Woreda",
                    "label": "Woreda",
                    "reqd": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1
                }
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "A2C Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "A2C Development Agent", "read": 1},
                {"role": "A2C Bank Agent", "read": 1},
                {"role": "A2C Bank Admin", "read": 1},
            ],
            "naming_rule": "Expression"
        })
        doc.insert(ignore_permissions=True)
        print("Created A2C Kebele DocType")

    # Data Migration: Get existing string data before converting fields
    banks = frappe.get_all("A2C Participating Bank", fields=["name", "registered_woreda_district", "registered_kebele_village"])
    farmers = frappe.get_all("A2C Farmer Profile", fields=["name", "region", "woreda", "kebele"])

    # Update DocType Fields
    bank_doc = frappe.get_doc("DocType", "A2C Participating Bank")
    for field in bank_doc.fields:
        if field.fieldname == "registered_woreda_district":
            field.fieldtype = "Link"
            field.options = "A2C Woreda"
        elif field.fieldname == "registered_kebele_village":
            field.fieldtype = "Link"
            field.options = "A2C Kebele"
    bank_doc.save(ignore_permissions=True)
    print("Updated A2C Participating Bank fields")

    farmer_doc = frappe.get_doc("DocType", "A2C Farmer Profile")
    for field in farmer_doc.fields:
        if field.fieldname == "region":
            field.fieldtype = "Link"
            field.options = "A2C Region"
        elif field.fieldname == "woreda":
            field.fieldtype = "Link"
            field.options = "A2C Woreda"
        elif field.fieldname == "kebele":
            field.fieldtype = "Link"
            field.options = "A2C Kebele"
    farmer_doc.save(ignore_permissions=True)
    print("Updated A2C Farmer Profile fields")

    frappe.db.commit()

    # Data Migration Execution
    for farmer in farmers:
        r = farmer.region
        w = farmer.woreda
        k = farmer.kebele
        
        region_id = None
        woreda_id = None
        kebele_id = None
        
        if r:
            if not frappe.db.exists("A2C Region", {"region_name": r}):
                reg = frappe.get_doc({"doctype": "A2C Region", "region_name": r})
                reg.insert(ignore_permissions=True)
                region_id = reg.name
            else:
                region_id = frappe.db.get_value("A2C Region", {"region_name": r}, "name")

        if w:
            if not region_id:
                if not frappe.db.exists("A2C Region", "Unknown"):
                    reg = frappe.get_doc({"doctype": "A2C Region", "region_name": "Unknown"})
                    reg.insert(ignore_permissions=True)
                region_id = "Unknown"
            
            if not frappe.db.exists("A2C Woreda", {"woreda_name": w, "region": region_id}):
                wor = frappe.get_doc({"doctype": "A2C Woreda", "woreda_name": w, "region": region_id})
                wor.insert(ignore_permissions=True)
                woreda_id = wor.name
            else:
                woreda_id = frappe.db.get_value("A2C Woreda", {"woreda_name": w, "region": region_id}, "name")
                
        if k:
            if not woreda_id:
                if not frappe.db.exists("A2C Woreda", {"woreda_name": "Unknown"}):
                    if not frappe.db.exists("A2C Region", "Unknown"):
                        reg = frappe.get_doc({"doctype": "A2C Region", "region_name": "Unknown"})
                        reg.insert(ignore_permissions=True)
                    wor = frappe.get_doc({"doctype": "A2C Woreda", "woreda_name": "Unknown", "region": "Unknown"})
                    wor.insert(ignore_permissions=True)
                woreda_id = frappe.db.get_value("A2C Woreda", {"woreda_name": "Unknown"}, "name")
            
            if not frappe.db.exists("A2C Kebele", {"kebele_name": k, "woreda": woreda_id}):
                keb = frappe.get_doc({"doctype": "A2C Kebele", "kebele_name": k, "woreda": woreda_id})
                keb.insert(ignore_permissions=True)
                kebele_id = keb.name
            else:
                kebele_id = frappe.db.get_value("A2C Kebele", {"kebele_name": k, "woreda": woreda_id}, "name")
                
        frappe.db.set_value("A2C Farmer Profile", farmer.name, "region", region_id)
        frappe.db.set_value("A2C Farmer Profile", farmer.name, "woreda", woreda_id)
        frappe.db.set_value("A2C Farmer Profile", farmer.name, "kebele", kebele_id)
        
    for bank in banks:
        w = bank.registered_woreda_district
        k = bank.registered_kebele_village
        woreda_id = None
        kebele_id = None
        
        if w:
            if not frappe.db.exists("A2C Region", "Unknown"):
                reg = frappe.get_doc({"doctype": "A2C Region", "region_name": "Unknown"})
                reg.insert(ignore_permissions=True)
                
            if not frappe.db.exists("A2C Woreda", {"woreda_name": w}):
                wor = frappe.get_doc({"doctype": "A2C Woreda", "woreda_name": w, "region": "Unknown"})
                wor.insert(ignore_permissions=True)
                woreda_id = wor.name
            else:
                woreda_id = frappe.db.get_value("A2C Woreda", {"woreda_name": w}, "name")
                
        if k:
            if not woreda_id:
                if not frappe.db.exists("A2C Woreda", {"woreda_name": "Unknown"}):
                    wor = frappe.get_doc({"doctype": "A2C Woreda", "woreda_name": "Unknown", "region": "Unknown"})
                    wor.insert(ignore_permissions=True)
                woreda_id = frappe.db.get_value("A2C Woreda", {"woreda_name": "Unknown"}, "name")
                
            if not frappe.db.exists("A2C Kebele", {"kebele_name": k, "woreda": woreda_id}):
                keb = frappe.get_doc({"doctype": "A2C Kebele", "kebele_name": k, "woreda": woreda_id})
                keb.insert(ignore_permissions=True)
                kebele_id = keb.name
            else:
                kebele_id = frappe.db.get_value("A2C Kebele", {"kebele_name": k, "woreda": woreda_id}, "name")
                
        frappe.db.set_value("A2C Participating Bank", bank.name, "registered_woreda_district", woreda_id)
        frappe.db.set_value("A2C Participating Bank", bank.name, "registered_kebele_village", kebele_id)

    frappe.db.commit()
    print("Migrated existing string data.")
