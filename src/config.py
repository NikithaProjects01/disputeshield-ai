from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
DB_PATH = DATA_DIR / "audit.db"
RANDOM_SEED = 42
CONFIDENCE_THRESHOLD = 0.55
SCORE_REVIEW_THRESHOLD = 50
CATEGORIES = [
    "Product not received", "Product not as described", "Duplicate charge",
    "Refund not processed", "Transaction not recognized",
    "Incorrect transaction amount", "Subscription cancellation dispute", "Other",
]

