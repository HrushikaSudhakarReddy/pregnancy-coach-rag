import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from sentence_transformers import SentenceTransformer

from src.nlp.intent_dataset import IntentDataset, LABELS
from src.utils.io import ensure_dir

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def embed_texts(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    return np.array(model.encode(texts, normalize_embeddings=True, convert_to_numpy=True))

def main(args):
    data_path = Path(args.data_csv)
    out_dir = ensure_dir(args.out_dir)

    ds = IntentDataset.from_csv(str(data_path))
    train_df, val_df, test_df = ds.train_val_test_split()

    le = LabelEncoder()
    le.fit(LABELS)

    st_model = SentenceTransformer(DEFAULT_EMBEDDING_MODEL)

    X_train = embed_texts(st_model, train_df["text"].tolist())
    y_train = le.transform(train_df["label"].tolist())
    X_val = embed_texts(st_model, val_df["text"].tolist())
    y_val = le.transform(val_df["label"].tolist())
    X_test = embed_texts(st_model, test_df["text"].tolist())
    y_test = le.transform(test_df["label"].tolist())

    clf = LogisticRegression(max_iter=2000, C=2.0, class_weight="balanced", solver="lbfgs")
    clf.fit(X_train, y_train)

    # Validation
    yv_pred = clf.predict(X_val)
    print("\n===== Validation Report =====")
    print(classification_report(y_val, yv_pred, target_names=le.classes_))
    print("Confusion matrix (val):\n", confusion_matrix(y_val, yv_pred))

    # Test
    yt_pred = clf.predict(X_test)
    print("\n===== Test Report =====")
    print(classification_report(y_test, yt_pred, target_names=le.classes_))
    print("Confusion matrix (test):\n", confusion_matrix(y_test, yt_pred))

    dump(
        {"label_encoder": le, "classifier": clf, "embedding_model_name": DEFAULT_EMBEDDING_MODEL},
        out_dir / "intent_classifier.joblib",
    )

    report = classification_report(y_test, yt_pred, target_names=le.classes_, output_dict=True)
    metrics = {
        "macro_f1": report["macro avg"]["f1-score"],
        "accuracy": report["accuracy"],
        "per_class_f1": {k: v["f1-score"] for k, v in report.items() if k in le.classes_},
    }
    pd.Series(metrics["per_class_f1"]).to_csv(out_dir / "per_class_f1.csv")
    with open(out_dir / "summary.txt", "w") as f:
        f.write(f"macro_f1={metrics['macro_f1']:.3f}\naccuracy={metrics['accuracy']:.3f}\n")
    print(f"\nSaved model to {out_dir / 'intent_classifier.joblib'}")
    print(f"Macro-F1 (test): {metrics['macro_f1']:.3f} | Acc: {metrics['accuracy']:.3f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_csv", default="backend/data/intents.csv")
    parser.add_argument("--out_dir", default="backend/models")
    args = parser.parse_args()
    main(args)
