import tempfile
from pathlib import Path
from src.evidence_engine import assess_evidence
from src.contradiction_detector import detect_contradictions
from src.scoring_engine import calculate_score
from src.recommendation_engine import recommend
from src.response_generator import generate_response
from src.audit_database import AuditDatabase
from src.document_extractor import extract_text

def test_mapping_and_missing():
    r=assess_evidence("Duplicate charge",["invoice"])
    assert "transaction_records" in r["required_missing"] and r["required_available"]==["invoice"]
def test_contradiction_amount_and_delivery():
    case={"transaction_amount":100,"transaction_id":"TX-1","merchant_statement":"It was delivered","transaction_date":"2026-01-01"}
    docs=[{"name":"proof.txt","fields":{"payment_amount":"120","delivery_status":"returned"}}]
    assert len(detect_contradictions(case,docs))==2
def test_score_bounds():
    e={"required_total":2,"required_available":["a"],"required_missing":["b"],"optional_available":[],"irrelevant":[]}
    assert 0 <= calculate_score(e,[],.8,[])["score"] <= 100
def test_low_confidence_escalates(): assert recommend(90,.2,[],[])["human_review_required"]
def test_response_never_invents_missing_evidence():
    e={"required_missing":["delivery_proof"]}
    text=generate_response({"case_id":"1"},{"reason":"Product not received"},e,[],{"recommendation":"Collect"})
    assert "CASE NOT READY" in text and "available evidence" not in text
def test_database_roundtrip(tmp_path):
    db=AuditDatabase(tmp_path/"audit.db")
    record={"case":{"case_id":"C1"},"score":{"score":60},"classification":{"reason":"Other"},"recommendation":{"recommendation":"Review","human_review_required":True}}
    assert db.save(record)==1 and db.list("C1")[0]["case_id"]=="C1"
def test_unreadable_upload():
    text,warning=extract_text("bad.xyz",b"x")
    assert text=="" and warning

