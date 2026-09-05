from pathlib import Path
import json, io
import pandas as pd
import plotly.express as px
import streamlit as st
from src.config import DATA_DIR
from src.document_extractor import extract_text, extract_fields
from src.pipeline import analyze
from src.audit_database import AuditDatabase

st.set_page_config(page_title="DisputeShield AI",page_icon="🛡️",layout="wide")
st.markdown("""
<style>
:root { --blue:#1688ff; }
.stApp { background:#071426; color:#f7fbff; }
.ds-card { background:#10243d; border:1px solid #224363; border-radius:14px; padding:18px; }
.notice { border-left:4px solid #1688ff; padding:10px; background:#10243d; }

/* Keep headings, form labels and helper text readable on the navy background. */
.stApp h1, .stApp h2, .stApp h3,
.stApp label, .stApp [data-testid="stWidgetLabel"],
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stMarkdownContainer"] p {
    color:#f7fbff !important;
}
.stApp [data-testid="stCaptionContainer"] p,
.stApp small { color:#b9cbe0 !important; }

/* Streamlit renders form controls on a light surface, so their text must be dark. */
.stApp input,
.stApp textarea,
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea,
.stApp [data-baseweb="select"] div,
.stApp [data-baseweb="select"] span {
    color:#071426 !important;
    -webkit-text-fill-color:#071426 !important;
    background-color:#f4f7fb !important;
    caret-color:#071426 !important;
}
.stApp input:focus,
.stApp textarea:focus,
.stApp input:-webkit-autofill,
.stApp input:-webkit-autofill:hover,
.stApp input:-webkit-autofill:focus {
    color:#071426 !important;
    -webkit-text-fill-color:#071426 !important;
    background-color:#f4f7fb !important;
    -webkit-box-shadow:0 0 0 1000px #f4f7fb inset !important;
    box-shadow:0 0 0 1000px #f4f7fb inset !important;
}
.stApp input::placeholder,
.stApp textarea::placeholder {
    color:#60738a !important;
    -webkit-text-fill-color:#60738a !important;
    opacity:1 !important;
}
.stApp [data-baseweb="input"],
.stApp [data-baseweb="input"] > div,
.stApp [data-baseweb="textarea"],
.stApp [data-baseweb="textarea"] > div,
.stApp [data-baseweb="select"] > div {
    background:#f4f7fb !important;
}
.stApp [data-testid="stTooltipIcon"] svg,
.stApp [data-testid="stWidgetLabel"] svg { fill:#9fc4ea !important; color:#9fc4ea !important; }
</style>
""",unsafe_allow_html=True)
db=AuditDatabase()
PAGES=["Overview","Analyze New Case","Evidence Report","Policy Evidence","Model Evaluation","Threshold and Cost Lab","Failure Analysis","Audit Trail","About and Responsible AI"]
with st.sidebar:
    st.title("🛡️ DisputeShield AI")
    page=st.radio("Workspace",PAGES)
    st.caption("Defensive decision support • Local-first • Human controlled")

def result():
    if "result" not in st.session_state: st.info("Analyze a case first to populate this page."); return None
    return st.session_state.result

if page=="Overview":
    st.title("Chargeback evidence intelligence")
    rows=pd.DataFrame(db.list())
    total=len(rows); strong=int((rows.score>=75).sum()) if total else 0; weak=int((rows.score<50).sum()) if total else 0; reviews=int((rows.review_status=="Pending").sum()) if total else 0
    cols=st.columns(5)
    for c,(label,value) in zip(cols,[("Cases analyzed",total),("Strong evidence",strong),("Weak evidence",weak),("Human review",reviews),("Average score",f"{rows.score.mean():.1f}" if total else "—")]): c.metric(label,value)
    st.markdown('<div class="notice">Scores support merchant decisions; they do not predict or guarantee chargeback outcomes.</div>',unsafe_allow_html=True)
    st.subheader("Recent case history"); st.dataframe(rows[["timestamp","case_id","reason","score","recommendation","review_status"]].head(10) if total else pd.DataFrame(),use_container_width=True)

elif page=="Analyze New Case":
    st.title("Analyze new case")
    st.caption("1 Enter details → 2 Upload evidence → 3 Review extraction → 4 Run analysis")
    with st.form("case"):
        a,b,c=st.columns(3)
        case_id=a.text_input("Case ID",value="CASE-001"); merchant_id=b.text_input("Merchant ID"); transaction_id=c.text_input("Transaction ID")
        customer_id=a.text_input("Customer ID"); transaction_date=b.date_input("Transaction date"); amount=c.number_input("Transaction amount (INR)",min_value=0.0)
        product=st.text_input("Product or service description"); dispute=st.text_area("Dispute description",help="Describe why the payment is disputed.")
        claim=st.text_area("Customer claim"); statement=st.text_area("Merchant statement"); refund=st.selectbox("Refund status",["Not refunded","Refunded","Pending","Unknown"])
        uploads=st.file_uploader("Evidence files",type=["pdf","txt","csv","png","jpg","jpeg"],accept_multiple_files=True)
        submitted=st.form_submit_button("Extract and review")
    if submitted:
        docs=[]
        for f in uploads:
            text,warning=extract_text(f.name,f.getvalue()); docs.append({"name":f.name,"size":f.size,"type":f.type,"text":text,"fields":extract_fields(text),"warning":warning})
        st.session_state.pending={"case":{"case_id":case_id,"merchant_id":merchant_id,"transaction_id":transaction_id,"customer_id":customer_id,"transaction_date":str(transaction_date),"transaction_amount":amount,"product_description":product,"dispute_description":dispute,"customer_claim":claim,"merchant_statement":statement,"refund_status":refund},"docs":docs}
    if "pending" in st.session_state:
        p=st.session_state.pending; st.subheader("Review extracted fields")
        corrected=[]; provided=[]
        type_options=["invoice","order_confirmation","delivery_proof","tracking_information","customer_communication","refund_policy","refund_transaction_record","transaction_records","separate_fulfilment_proof","product_description","billing_delivery_information","device_session_information","subscription_terms","cancellation_record","additional_document"]
        for i,d in enumerate(p["docs"]):
            with st.expander(d["name"],expanded=True):
                dtype=st.selectbox("Evidence type",type_options,key=f"dt{i}"); provided.append(dtype)
                if d["warning"]: st.warning(d["warning"])
                fields=st.text_area("Extracted fields (JSON; correct if needed)",json.dumps(d["fields"],indent=2),key=f"f{i}")
                try: d["fields"]=json.loads(fields)
                except json.JSONDecodeError: st.error("Invalid JSON; original extraction retained.")
                corrected.append(d)
        if st.button("Run complete analysis",type="primary"):
            try:
                r=analyze(p["case"],corrected,provided); st.session_state.result=r; db.save(r); st.success("Analysis completed and saved to the audit trail."); st.rerun()
            except Exception as exc: st.error(f"Analysis could not run safely: {exc}")
    if "result" in st.session_state:
        r=st.session_state.result; st.subheader("Latest result")
        x,y,z=st.columns(3); x.metric("Reason",r["classification"]["reason"]); y.metric("Confidence",f"{r['classification']['confidence']:.1%}"); z.metric("Evidence score",r["score"]["score"])
        st.write("Alternative:",r["classification"]["alternative"],"• Influential words:",", ".join(r["classification"]["features"]) or "None")
        st.warning(r["recommendation"]["recommendation"]); st.code(r["response"])

elif page=="Evidence Report":
    r=result()
    if r:
        st.title("Evidence report"); st.metric("Evidence Strength Score",r["score"]["score"],r["score"]["category"])
        st.plotly_chart(px.bar(x=list(r["score"]["components"]),y=list(r["score"]["components"].values()),labels={"x":"Component","y":"Points"}),use_container_width=True)
        a,b=st.columns(2); a.success("Available: "+", ".join(r["evidence"]["required_available"])); b.error("Missing: "+", ".join(r["evidence"]["required_missing"]))
        st.subheader("Contradictions"); st.dataframe(pd.DataFrame(r["contradictions"]),use_container_width=True)
        st.subheader("Next actions"); st.write("\n".join("- "+x for x in r["recommendation"]["actions"]))

elif page=="Policy Evidence":
    r=result()
    if r:
        st.title("Retrieved policy evidence")
        for p in r["policies"]: st.markdown(f"**{p['source']} — section {p['section']}** · relevance {p['relevance']:.2f}\n\n{p['text']}")
        st.info("Policy passages are retrieved verbatim from local sample or uploaded sources and are supporting context only.")

elif page=="Model Evaluation":
    st.title("Held-out model evaluation")
    path=DATA_DIR/"evaluation_report.json"
    if not path.exists(): st.warning("Run `python scripts/evaluate_model.py` to generate genuine held-out metrics.")
    else:
        rep=json.loads(path.read_text()); c=st.columns(4); c[0].metric("Accuracy",f"{rep['accuracy']:.1%}"); c[1].metric("Test cases",rep["cases"]); c[2].metric("Review rate",f"{rep['human_review_escalation_rate']:.1%}"); c[3].metric("Estimated cost",f"₹{rep['estimated_cost']:,.0f}")
        cls=pd.DataFrame(rep["classification_report"]).T; st.dataframe(cls,use_container_width=True)
        st.plotly_chart(px.imshow(rep["confusion_matrix"],x=rep["classes"],y=rep["classes"],labels={"x":"Predicted","y":"Actual","color":"Cases"}),use_container_width=True)

elif page=="Threshold and Cost Lab":
    st.title("Threshold and cost lab"); path=DATA_DIR/"test.csv"
    if not path.exists(): st.warning("Generate and train the dataset first.")
    else:
        import joblib, numpy as np
        model=joblib.load("models/dispute_classifier.joblib"); df=pd.read_csv(path); conf=model.predict_proba(df.dispute_description).max(axis=1); truth=df.expected_human_review.astype(bool).to_numpy()
        loss=st.number_input("Average chargeback loss (INR)",value=float(df.transaction_amount.mean())); manual=st.number_input("Manual review cost (INR)",value=300.0)
        rows=[]
        for t in np.arange(.3,.91,.05):
            review=conf<t; fp=int((review&~truth).sum()); fn=int((~review&truth).sum()); tp=int((review&truth).sum())
            rows.append({"threshold":t,"precision":tp/max(1,tp+fp),"recall":tp/max(1,tp+fn),"false_positives":fp,"false_negatives":fn,"estimated_cost":fn*loss+fp*manual,"review_workload":review.mean()})
        lab=pd.DataFrame(rows); st.plotly_chart(px.line(lab,x="threshold",y=["precision","recall","review_workload"]),use_container_width=True); st.plotly_chart(px.line(lab,x="threshold",y="estimated_cost"),use_container_width=True); st.dataframe(lab,use_container_width=True)

elif page=="Failure Analysis":
    st.title("Failure analysis")
    path=DATA_DIR/"failure_cases.csv"; st.subheader("Misclassified held-out cases")
    st.dataframe(pd.read_csv(path) if path.exists() else pd.DataFrame(),use_container_width=True)
    st.subheader("Adversarial safety cases"); adv=json.loads((DATA_DIR/"sample_cases/adversarial_cases.json").read_text())
    for x in adv: st.markdown(f"**{x['name']}** — {x['description']}  \nLikely risk: misleading or conflicting evidence. Suggested handling: deterministic cross-check and human escalation.")

elif page=="Audit Trail":
    st.title("Audit trail"); query=st.text_input("Filter by case ID"); rows=db.list(query); frame=pd.DataFrame(rows); st.dataframe(frame.drop(columns=["payload"],errors="ignore"),use_container_width=True)
    if rows:
        st.download_button("Export CSV",frame.to_csv(index=False),"audit.csv","text/csv"); st.download_button("Export JSON",frame.to_json(orient="records",indent=2),"audit.json","application/json")
        with st.form("review"):
            rid=st.selectbox("Record ID",[x["id"] for x in rows]); status=st.selectbox("Final decision",["Approved","Rejected","Pending"]); comments=st.text_area("Reviewer comments")
            if st.form_submit_button("Record review"): db.review(rid,status,comments); st.success("Review recorded.")

else:
    st.title("About and Responsible AI")
    st.markdown("""DisputeShield AI is an independent hackathon prototype for defensive merchant decision support. It is not an official Razorpay product and does not imply Razorpay endorsement.

**Safeguards:** no automatic submission or customer blocking; no fabricated evidence; grounded deterministic drafts; visible contradictions; configurable escalation; auditable decisions; local-first processing; explicit human control.

**Limitations:** synthetic training data does not represent production traffic; OCR quality depends on local Tesseract availability; rule-based extraction and contradiction detection will not cover every document format; the evidence score does not guarantee an outcome.""")
