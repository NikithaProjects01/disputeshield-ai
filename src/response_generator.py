def generate_response(case, classification, evidence, documents, recommendation):
    if evidence["required_missing"]:
        return "CASE NOT READY — PREPARATION CHECKLIST\n\n" + "\n".join(f"- Collect {x.replace('_',' ')}" for x in evidence["required_missing"]) + "\n\nMerchant review is required before submission."
    names = [d["name"] for d in documents if not d.get("warning")]
    amount = case.get("transaction_amount")
    return (f"Draft chargeback response — merchant review required\n\n"
            f"Case {case.get('case_id', '[uncertain]')} concerns a {classification['reason'].lower()} dispute for transaction "
            f"{case.get('transaction_id', '[uncertain]')} of INR {amount if amount is not None else '[uncertain]'}. "
            f"The available evidence reviewed for this draft is: {', '.join(names) if names else '[no verified documents]'}. "
            f"Merchant statement: {case.get('merchant_statement') or '[not provided]'}.\n\n"
            f"Recommendation: {recommendation['recommendation']}. This draft uses only supplied case data and must be checked by the merchant before submission.")

