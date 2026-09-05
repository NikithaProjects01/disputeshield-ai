from .config import CONFIDENCE_THRESHOLD, SCORE_REVIEW_THRESHOLD

def recommend(score, confidence, missing, contradictions, unreadable=0):
    major = any(x["severity"] == "major" for x in contradictions)
    review = confidence < CONFIDENCE_THRESHOLD or score < SCORE_REVIEW_THRESHOLD or major or unreadable > 0
    if confidence < CONFIDENCE_THRESHOLD or unreadable: title = "Escalate for human review"
    elif major: title = "Resolve contradictions"
    elif missing: title = "Collect additional evidence"
    else: title = "Ready for merchant review"
    actions = [f"Obtain {x.replace('_',' ')}." for x in missing]
    if major: actions.append("Resolve each major contradiction against source records.")
    if review: actions.append("Have an authorized reviewer verify the case before submission.")
    return {"recommendation": title, "human_review_required": review, "actions": actions or ["Review the grounded draft and source documents."]}

