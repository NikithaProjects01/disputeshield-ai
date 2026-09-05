from __future__ import annotations

def calculate_score(evidence: dict, contradictions: list[dict], confidence: float, policies: list[dict], unreadable: int = 0) -> dict:
    total = max(1, evidence["required_total"])
    completeness = len(evidence["required_available"]) / total
    consistency = max(0.0, 1 - .4 * sum(x["severity"] == "major" for x in contradictions) - .15 * sum(x["severity"] != "major" for x in contradictions))
    relevance = (len(evidence["required_available"]) + len(evidence["optional_available"])) / max(1, len(evidence["required_available"]) + len(evidence["optional_available"]) + len(evidence["irrelevant"]))
    policy = min(1.0, max([p.get("relevance", 0) for p in policies], default=0) * 2)
    components = {"Required evidence completeness": 40*completeness, "Evidence consistency": 25*consistency, "Document relevance": 15*relevance, "Classification confidence": 10*confidence, "Policy support": 10*policy}
    penalties = {"critical_missing": 5 * len(evidence["required_missing"]), "major_contradictions": 8 * sum(x["severity"] == "major" for x in contradictions), "unreadable_documents": 5 * unreadable}
    score = max(0, min(100, sum(components.values()) - sum(penalties.values())))
    return {"score": round(score, 1), "components": {k: round(v, 1) for k,v in components.items()}, "penalties": penalties, "category": "Strong evidence" if score >= 75 else "Needs improvement" if score >= 50 else "Weak evidence"}

