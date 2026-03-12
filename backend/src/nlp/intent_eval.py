import argparse
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sentence_transformers import SentenceTransformer
from joblib import load
from src.nlp.intent_dataset import IntentDataset, LABELS

def main(args):
    ds = IntentDataset.from_csv(args.data_csv)
    _, _, test_df = ds.train_val_test_split()
    bundle = load(args.model_path)
    clf = bundle["classifier"]; le = bundle["label_encoder"]
    embedder = SentenceTransformer(bundle["embedding_model_name"])

    X_test = embedder.encode(test_df["text"].tolist(), normalize_embeddings=True, convert_to_numpy=True)
    y_test = le.transform(test_df["label"].tolist())
    y_pred = clf.predict(X_test)

    cm = confusion_matrix(y_test, y_pred, labels=range(len(LABELS)))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=LABELS)
    disp.plot(xticks_rotation=45)
    plt.tight_layout()
    plt.savefig("backend/models/confusion_matrix.png", dpi=180)
    print("Saved to backend/models/confusion_matrix.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_csv", default="backend/data/intents.csv")
    parser.add_argument("--model_path", default="backend/models/intent_classifier.joblib")
    args = parser.parse_args()
    main(args)
