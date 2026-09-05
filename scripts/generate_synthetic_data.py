from pathlib import Path
import sys, random
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import DATA_DIR, CATEGORIES, RANDOM_SEED

TEMPLATES = {
"Product not received":["my parcel has not arrived", "order never delivered although tracking says pending", "did not receive the product"],
"Product not as described":["item is different from its description", "product quality and colour do not match", "service was not as advertised"],
"Duplicate charge":["charged twice for the same order", "duplicate payment appears on my card", "same transaction debited two times"],
"Refund not processed":["refund promised but not received", "merchant has not processed my refund", "return completed but money not credited"],
"Transaction not recognized":["I do not recognize this payment", "unknown purchase on my statement", "I never authorized this transaction"],
"Incorrect transaction amount":["charged the wrong amount", "invoice total differs from debit", "amount taken is higher than agreed"],
"Subscription cancellation dispute":["charged after cancelling subscription", "membership was cancelled but billing continued", "renewal debit after cancellation"],
"Other":["I have another issue with this transaction", "payment dispute needs investigation", "unclear problem with this purchase"],
}
NOISE=["please help", "urgent", "merchant disagrees", "ref tx", "details missing", "custmer says", "possible mix up"]

def typo(s, rng):
    if len(s)>10:
        i=rng.randrange(2,len(s)-2); return s[:i]+s[i+1:]
    return s

def main():
    rng=random.Random(RANDOM_SEED); rows=[]
    for i in range(1600):
        reason=CATEGORIES[i%len(CATEGORIES)]; text=rng.choice(TEMPLATES[reason])
        if rng.random()<.35: text += ". " + rng.choice(NOISE)
        if rng.random()<.12: text=typo(text,rng)
        missing=rng.random()<.35; contradiction=rng.random()<.18
        amount=round(rng.uniform(199,75000),2)
        rows.append({"case_id":f"SYN-{i+1:05}","transaction_id":f"TXN-{rng.randrange(100000,999999)}","dispute_description":text,"ground_truth_reason":reason,"transaction_amount":amount,"missing_document":missing,"contradiction":contradiction,"expected_human_review":missing or contradiction or "unclear" in text,"synthetic":True})
    rng.shuffle(rows); df=pd.DataFrame(rows); DATA_DIR.mkdir(exist_ok=True)
    for name, frame in (("train",df.iloc[:1120]),("validation",df.iloc[1120:1360]),("test",df.iloc[1360:])): frame.to_csv(DATA_DIR/f"{name}.csv",index=False)
    # an intentionally imbalanced variant
    pd.concat([df[df.ground_truth_reason=="Product not received"]]*3+[df]).sample(frac=1,random_state=RANDOM_SEED).to_csv(DATA_DIR/"imbalanced.csv",index=False)
    print("Generated 1,600 synthetic cases: 1,120 train / 240 validation / 240 test")
if __name__=="__main__": main()

