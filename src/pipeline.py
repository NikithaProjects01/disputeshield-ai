from .dispute_classifier import DisputeClassifier
from .evidence_engine import assess_evidence
from .contradiction_detector import detect_contradictions
from .policy_retriever import retrieve_policies
from .scoring_engine import calculate_score
from .recommendation_engine import recommend
from .response_generator import generate_response

def analyze(case, documents, provided):
    clf=DisputeClassifier().predict(" ".join([case.get("dispute_description", ""), case.get("customer_claim", "")]))
    evidence=assess_evidence(clf["reason"], provided)
    contradictions=detect_contradictions(case, documents)
    policies=retrieve_policies(case.get("dispute_description", "") + " " + clf["reason"])
    unreadable=sum(bool(d.get("warning")) for d in documents)
    score=calculate_score(evidence, contradictions, clf["confidence"], policies, unreadable)
    rec=recommend(score["score"],clf["confidence"],evidence["required_missing"],contradictions,unreadable)
    response=generate_response(case,clf,evidence,documents,rec)
    return {"case":case,"documents":documents,"classification":clf,"evidence":evidence,"contradictions":contradictions,"policies":policies,"score":score,"recommendation":rec,"response":response}
