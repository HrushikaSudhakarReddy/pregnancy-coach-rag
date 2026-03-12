import argparse
from pathlib import Path
import numpy as np, pandas as pd
from joblib import dump
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer

DEFAULT_EMB = "all-MiniLM-L6-v2"

def embed(model, texts):
    return model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)

def main(data_csv: str, out_dir: str):
    df = pd.read_csv(data_csv).dropna(subset=["text","label"])
    df["text"] = df["text"].astype(str).str.strip()
    df["label"]= df["label"].str.strip().str.lower()

    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])
    le = LabelEncoder().fit(["unsafe","safe"])  # class order fixed

    st = SentenceTransformer(DEFAULT_EMB)
    Xtr = embed(st, train["text"].tolist()); ytr = le.transform(train["label"].tolist())
    Xte = embed(st, test["text"].tolist());  yte = le.transform(test["label"].tolist())

    clf = LogisticRegression(max_iter=2000, C=2.0, class_weight="balanced", solver="lbfgs").fit(Xtr, ytr)

    ypred = clf.predict(Xte)
    print("\n===== Safety Test Report =====")
    print(classification_report(yte, ypred, target_names=le.classes_))

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    dump({"label_encoder": le, "classifier": clf, "embedding_model_name": DEFAULT_EMB},
         Path(out_dir)/"safety_classifier.joblib")
    print("Saved:", Path(out_dir)/"safety_classifier.joblib")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_csv", default="backend/data/safety.csv")
    ap.add_argument("--out_dir",  default="backend/models")
    args = ap.parse_args()
    main(args.data_csv, args.out_dir)
