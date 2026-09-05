from __future__ import annotations

REQUIREMENTS = {
 "Product not received": (["invoice", "order_confirmation", "delivery_proof", "tracking_information"], ["customer_communication"]),
 "Product not as described": (["invoice", "order_confirmation", "product_description"], ["customer_communication", "delivery_proof"]),
 "Duplicate charge": (["invoice", "transaction_records", "separate_fulfilment_proof"], ["customer_communication"]),
 "Refund not processed": (["refund_policy", "refund_transaction_record", "customer_communication"], ["invoice"]),
 "Transaction not recognized": (["order_confirmation", "billing_delivery_information"], ["device_session_information", "customer_communication"]),
 "Incorrect transaction amount": (["invoice", "transaction_records"], ["order_confirmation", "customer_communication"]),
 "Subscription cancellation dispute": (["subscription_terms", "cancellation_record", "transaction_records"], ["customer_communication"]),
 "Other": (["invoice", "customer_communication"], ["order_confirmation"]),
}

def assess_evidence(reason: str, provided: list[str]) -> dict:
    required, optional = REQUIREMENTS.get(reason, REQUIREMENTS["Other"])
    present = set(provided)
    return {
        "required_available": [x for x in required if x in present],
        "required_missing": [x for x in required if x not in present],
        "optional_available": [x for x in optional if x in present],
        "irrelevant": sorted(present - set(required) - set(optional)),
        "required_total": len(required),
    }

