from typing import Literal, Dict
import numpy as np
from joblib import load
from sentence_transformers import SentenceTransformer

IntentLabel = Literal["workout", "meal", "vitamins", "safety", "general"]

class IntentClassifier:
    def __init__(self, model_path: str):
        bundle = load(model_path)
        self.le = bundle["label_encoder"]
        self.clf = bundle["classifier"]
        self.emb_name = bundle["embedding_model_name"]
        self.embedder = SentenceTransformer(self.emb_name)

    def predict_proba(self, text: str) -> Dict[IntentLabel, float]:
        emb = self.embedder.encode([text], normalize_embeddings=True, convert_to_numpy=True)
        probs = self.clf.predict_proba(emb)[0]
        labels = self.le.inverse_transform(np.arange(len(probs)))
        return {label: float(p) for label, p in zip(labels, probs)}

    def predict(self, text: str, threshold: float = 0.40) -> tuple[IntentLabel, float]:
        prob_map = self.predict_proba(text)
        label, prob = max(prob_map.items(), key=lambda kv: kv[1])
        if prob < threshold:
            return "general", prob
        return label, prob
