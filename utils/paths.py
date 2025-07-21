from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "database" / "ecommerce.db"
CONFIG_DEFAULT = ROOT / "config_example.yaml"
