from __future__ import annotations
from datetime import datetime

def _date(value):
    if not value: return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try: return datetime.strptime(str(value), fmt).date()
        except ValueError: pass
    return None

def detect_contradictions(case: dict, documents: list[dict]) -> list[dict]:
    issues = []
    def add(fields, values, docs, severity, explanation):
        issues.append({"fields": fields, "values": values, "documents": docs, "severity": severity, "explanation": explanation})
    statement = str(case.get("merchant_statement", "")).lower()
    statuses = [(d.get("name", "document"), str(d.get("fields", {}).get("delivery_status", "")).lower()) for d in documents]
    for name, status in statuses:
        if "delivered" in statement and status in {"failed", "returned"}:
            add(["merchant_statement", "delivery_status"], ["delivered", status], ["case", name], "major", "The merchant statement says delivered, but delivery evidence shows an unsuccessful outcome.")
    if "not refunded" in statement and (case.get("refund_status") == "Refunded" or any(d.get("fields", {}).get("refund_date") for d in documents)):
        add(["merchant_statement", "refund_status"], ["not refunded", "refund record exists"], ["case", "uploaded evidence"], "major", "The statement conflicts with refund information.")
    tx_amount = float(case.get("transaction_amount", 0) or 0)
    for d in documents:
        raw = d.get("fields", {}).get("payment_amount")
        if raw:
            try:
                amount = float(str(raw).replace(",", ""))
                if abs(amount - tx_amount) > .01: add(["payment_amount", "transaction_amount"], [amount, tx_amount], [d.get("name"), "case"], "major", "The document amount differs from the transaction amount.")
            except ValueError: pass
        doc_txn = d.get("fields", {}).get("transaction_id")
        if doc_txn and case.get("transaction_id") and doc_txn != case["transaction_id"]:
            add(["transaction_id"], [doc_txn, case["transaction_id"]], [d.get("name"), "case"], "major", "Transaction identifiers do not match.")
        f = d.get("fields", {})
        if _date(f.get("delivery_date")) and _date(f.get("order_date")) and _date(f["delivery_date"]) < _date(f["order_date"]):
            add(["delivery_date", "order_date"], [f["delivery_date"], f["order_date"]], [d.get("name")], "major", "Delivery is dated before the order.")
        if _date(f.get("refund_date")) and _date(case.get("transaction_date")) and _date(f["refund_date"]) < _date(case["transaction_date"]):
            add(["refund_date", "transaction_date"], [f["refund_date"], str(case["transaction_date"])], [d.get("name"), "case"], "major", "Refund is dated before payment.")
    values = {}
    for d in documents:
        for key, value in d.get("fields", {}).items(): values.setdefault(key, []).append((d.get("name"), str(value)))
    for key, pairs in values.items():
        unique = set(v for _, v in pairs if v)
        if len(unique) > 1 and key in {"order_id", "transaction_id", "payment_amount", "delivery_status"}:
            add([key], sorted(unique), [n for n, _ in pairs], "major", f"Uploaded documents contain different {key.replace('_', ' ')} values.")
    return issues

