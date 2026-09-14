"""Configuração, serialização e rastreabilidade compartilhadas."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
YEARS = tuple(range(2020, 2027))
PORTAL = "https://dadosabertos.saude.gov.br/dataset/bps"
RAW = ROOT / "data/raw"
PROCESSED = ROOT / "data/processed"
EVIDENCE = ROOT / "docs/evidence"

def setup():
    for folder in (RAW, PROCESSED, EVIDENCE):
        folder.mkdir(parents=True, exist_ok=True)

def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")

def sha256(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def config():
    return json.loads((ROOT / "project.json").read_text(encoding="utf-8"))

def output_csv():
    return PROCESSED / f"BPS_20_26_{config()['student_slug']}.csv"

