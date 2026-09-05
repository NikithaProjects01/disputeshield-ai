from __future__ import annotations
import joblib, numpy as np
from .config import MODEL_DIR

class DisputeClassifier:
    def __init__(self, path=None):
        self.path = path or MODEL_DIR / "dispute_classifier.joblib"
        self.pipeline = joblib.load(self.path) if self.path.exists() else None

    def predict(self, text: str) -> dict:
        if self.pipeline is None: raise FileNotFoundError("Train the classifier first: python scripts/train_model.py")
        probs = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_
        order = np.argsort(probs)[::-1]
        vectorizer, model = self.pipeline.named_steps["tfidf"], self.pipeline.named_steps["clf"]
        row = vectorizer.transform([text])
        ci = list(classes).index(classes[order[0]])
        contributions = row.multiply(model.coef_[ci]).toarray()[0]
        names = vectorizer.get_feature_names_out()
        top = np.argsort(contributions)[::-1][:5]
        return {"reason": classes[order[0]], "confidence": float(probs[order[0]]), "alternative": classes[order[1]], "alternative_confidence": float(probs[order[1]]), "features": [names[i] for i in top if contributions[i] > 0]}

