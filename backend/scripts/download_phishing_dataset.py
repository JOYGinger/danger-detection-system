from __future__ import annotations

from pathlib import Path

import pandas as pd

URL = "https://huggingface.co/datasets/zefang-liu/phishing-email-dataset/resolve/main/Phishing_Email.csv?download=true"
OUT = Path(__file__).resolve().parents[1] / "data" / "phishing_email_dataset.csv"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(URL)
    df = df.rename(columns={"Email Text": "text", "Email Type": "label"})
    df[["text", "label"]].to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"saved {len(df)} rows to {OUT}")


if __name__ == "__main__":
    main()
