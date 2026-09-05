from pathlib import Path
import sys, joblib, pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from src.config import DATA_DIR, MODEL_DIR, RANDOM_SEED

def main():
    df=pd.read_csv(DATA_DIR/"train.csv")
    pipeline=Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2),min_df=2,sublinear_tf=True)),("clf",LogisticRegression(max_iter=1000,class_weight="balanced",random_state=RANDOM_SEED))])
    pipeline.fit(df.dispute_description,df.ground_truth_reason); MODEL_DIR.mkdir(exist_ok=True); joblib.dump(pipeline,MODEL_DIR/"dispute_classifier.joblib")
    print(f"Trained on {len(df)} synthetic cases")
if __name__=="__main__": main()

