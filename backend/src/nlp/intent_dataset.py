from dataclasses import dataclass
from typing import Tuple
import pandas as pd
from sklearn.model_selection import train_test_split

LABELS = ["workout", "meal", "vitamins", "safety", "general"]

@dataclass
class IntentDataset:
    df: pd.DataFrame

    @classmethod
    def from_csv(cls, path: str) -> "IntentDataset":
        df = pd.read_csv(path)
        df = df.dropna(subset=["text", "label"])
        df["text"] = df["text"].astype(str).str.strip()
        df["label"] = df["label"].str.lower().str.strip()
        df = df[df["label"].isin(LABELS)]
        return cls(df)

    def train_val_test_split(
        self, test_size: float = 0.15, val_size: float = 0.15,
        random_state: int = 42, stratify: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        df = self.df.copy()
        strat = df["label"] if stratify else None
        from sklearn.model_selection import train_test_split
        train_df, temp_df = train_test_split(
            df, test_size=(test_size + val_size), random_state=random_state, stratify=strat
        )
        strat_temp = temp_df["label"] if stratify else None
        rel_val = val_size / (test_size + val_size)
        val_df, test_df = train_test_split(
            temp_df, test_size=(1 - rel_val), random_state=random_state, stratify=strat_temp
        )
        return train_df, val_df, test_df
