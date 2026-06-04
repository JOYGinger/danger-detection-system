from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ml.phishing_model import train_model_from_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Train phishing email hybrid model")
    parser.add_argument("--csv", required=True, help="Path to phishing email CSV")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        fallback = ROOT / args.csv
        if fallback.exists():
            csv_path = fallback
        else:
            data_fallback = ROOT / "data" / csv_path.name
            if data_fallback.exists():
                csv_path = data_fallback

    metrics = train_model_from_csv(str(csv_path))
    print(metrics)


if __name__ == "__main__":
    main()
