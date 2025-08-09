import frappe

def execute(filters=None):
    columns = [
        {"label": "Purchase Receipt", "fieldname": "purchase_receipt", "fieldtype": "Data", "width": 150},
        {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 90},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
        {"label": "Qty Received", "fieldname": "qty_received", "fieldtype": "Float", "width": 100},
        {"label": "Manufacturing Item", "fieldname": "mfg_item", "fieldtype": "Data", "width": 150},
        {"label": "Work Order Number", "fieldname": "work_order", "fieldtype": "Data", "width": 150},
        {"label": "Date of Desp.", "fieldname": "date_of_desp", "fieldtype": "Date", "width": 90},
        {"label": "Grn.No", "fieldname": "grn_no", "fieldtype": "Data", "width": 100},
        {"label": "Inv.Qty", "fieldname": "inv_qty", "fieldtype": "Float", "width": 90},
        {"label": "Qty.cons", "fieldname": "qty_cons", "fieldtype": "Float", "width": 90},
        {"label": "Balance", "fieldname": "balance", "fieldtype": "Float", "width": 90},
    ]

    purchase_receipts = frappe.db.sql("""
        SELECT
            pr.name as purchase_receipt,
            pr.posting_date,
            pri.item_code,
            pri.qty as qty_received
        FROM
            `tabPurchase Receipt` pr
        JOIN
            `tabPurchase Receipt Item` pri ON pri.parent = pr.name
        WHERE
            pr.docstatus = 1
        ORDER BY pr.posting_date, pr.name
    """, as_dict=True)

    data = []
    for pr in purchase_receipts:
        data.append({
            "purchase_receipt": pr.purchase_receipt,
            "posting_date": pr.posting_date,
            "item_code": pr.item_code,
            "qty_received": pr.qty_received,
            "mfg_item": "",
            "work_order": "",
            "date_of_desp": None,
            "grn_no": "",
            "inv_qty": None,
            "qty_cons": None,
            "balance": None,
        })

        work_orders = frappe.db.sql("""
            SELECT
                woi.item_code as mfg_item,
                wo.name as work_order,
                wo.scheduled_start_date as date_of_desp,
                '' as grn_no,
                woi.qty as inv_qty,
                woi.consumed_qty as qty_cons,
                (wo.produced_qty - woi.consumed_qty) as balance
            FROM
                `tabWork Order Item` woi
            JOIN
                `tabWork Order` wo ON wo.name = woi.parent
            WHERE
                woi.item_code = %s
                AND wo.status = 'Completed'
            ORDER BY wo.scheduled_start_date
        """, pr.item_code, as_dict=True)

        for wo in work_orders:
            data.append({
                "purchase_receipt": "",
                "posting_date": None,
                "item_code": "",
                "qty_received": None,
                "mfg_item": wo.mfg_item,
                "work_order": wo.work_order,
                "date_of_desp": wo.date_of_desp,
                "grn_no": wo.grn_no,
                "inv_qty": wo.inv_qty,
                "qty_cons": wo.qty_cons,
                "balance": wo.balance,
            })

    return columns, data

