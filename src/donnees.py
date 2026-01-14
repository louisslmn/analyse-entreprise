"""
donnees.py
==========

Chargement et préparation des jeux de données (exemple).
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def charger_donnees_financieres(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["annee"] = df["annee"].astype(int)
    return df.sort_values(["entreprise", "annee"]).reset_index(drop=True)


def charger_donnees_extra_financieres(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df.sort_values(["entreprise"]).reset_index(drop=True)
