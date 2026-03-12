from typing import Literal, Dict
import numpy as np
from joblib import load
from sentence_transformers import SentenceTransformer

SafetyLabel = Literal["unsafe","safe"]

class SafetyClassifier:
    def __init__(self, model_path: str):
        b = load(model_path)
        self.le = b["label_encoder"]
        self.clf = b["classifier"]
        self.emb = SentenceTransformer(b["embedding_model_name"])

    def predict_proba(self, text: str) -> Dict[SafetyLabel, float]:
        X = self.emb.encode([text], normalize_embeddings=True, convert_to_numpy=True)
        probs = self.clf.predict_proba(X)[0]
        labels = self.le.inverse_transform(np.arange(len(probs)))
        return {label: float(p) for label, p in zip(labels, probs)}

    def predict(self, text: str, thresh: float = 0.35) -> tuple[SafetyLabel, float]:
        pm = self.predict_proba(text)
        label, p = max(pm.items(), key=lambda kv: kv[1])
        # Conservative: if low confidence and predicted safe, treat as unsafe
        if p < thresh and label == "safe":
            return "unsafe", p
        return label, p
