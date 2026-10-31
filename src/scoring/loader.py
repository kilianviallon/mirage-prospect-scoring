"""Lecture de la configuration et des données, ajout d'une entreprise."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "scoring.yaml"
COMPANIES_PATH = ROOT / "data" / "companies.yaml"
FALSE_POSITIVES_PATH = ROOT / "data" / "false_positives.yaml"


def load_config(path=CONFIG_PATH):
    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    total = sum(c["weight"] for c in config["criteria"].values())
    if total != 100:
        raise ValueError(f"La somme des poids doit faire 100 (actuellement {total}).")
    return config


def load_companies(path=COMPANIES_PATH):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def append_company(company, path=COMPANIES_PATH):
    """Ajoute une entreprise à la fin du fichier, sans réécrire les autres
    (les commentaires et la mise en forme existants sont conservés)."""
    existing = {c["name"].strip().lower() for c in load_companies(path)}
    if company["name"].strip().lower() in existing:
        raise ValueError(f"« {company['name']} » existe déjà dans le fichier.")
    block = yaml.safe_dump([company], allow_unicode=True, sort_keys=False, width=1000)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + block)
