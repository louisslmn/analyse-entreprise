"""
scoring.py
==========

Construction d'un score "screener" paramétrable.

Idée :
- On choisit des indicateurs (ratios)
- On les normalise (0..100) par classement relatif (robuste en présence d'unités différentes)
- On agrège via des poids

On ajoute une composante extra-financière (carbone / CA vert / ESG) pour
montrer un intérêt "finance durable" sans tomber dans un projet trop lourd.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


def _score_rang(valeurs: pd.Series, sens: str = "max") -> pd.Series:
    """
    Score 0..100 basé sur le rang (percentile), plus robuste qu'une normalisation min/max.

    sens="max" : plus grand = meilleur
    sens="min" : plus petit = meilleur
    """
    s = valeurs.copy()
    # On gère les NaN : score neutre 50
    mask = s.notna()
    if mask.sum() < 2:
        return pd.Series(50.0, index=s.index)

    ranks = s[mask].rank(pct=True)  # 0..1
    if sens == "min":
        ranks = 1.0 - ranks

    out = pd.Series(50.0, index=s.index)
    out.loc[mask] = 100.0 * ranks
    return out


@dataclass(frozen=True)
class Ponderations:
    """
    Poids (somme libre) pour les familles de critères.

    Les poids seront renormalisés dans l'app.
    """
    profitabilite: float = 1.0
    croissance: float = 1.0
    solidite: float = 1.0
    liquidite: float = 0.7
    cashflow: float = 1.0
    extra_financier: float = 0.8


def construire_scores(df_dernier: pd.DataFrame, df_extra: pd.DataFrame, pond: Ponderations) -> pd.DataFrame:
    """
    Construit un tableau de scoring par entreprise (dernier exercice).

    df_dernier : dataframe ratios (dernier exercice par entreprise)
    df_extra : table extra-financière (une ligne par entreprise)
    """
    d = df_dernier.merge(df_extra, on="entreprise", how="left")

    # ---- Scores par famille ----
    # Profitabilité : marge + ROE
    s_profit = 0.6 * _score_rang(d["marge_nette"], "max") + 0.4 * _score_rang(d["roe"], "max")

    # Croissance : croissance CA (si NaN -> neutre)
    s_growth = _score_rang(d["croissance_ca"], "max")

    # Solidité : dette/équity plus faible = mieux
    s_solid = _score_rang(d["debt_to_equity"], "min")

    # Liquidité : current ratio (trop faible = risque, trop élevé peut signifier inefficacité)
    # On score "max" mais on cappe l'effet des valeurs extrêmes via log.
    s_liq = _score_rang(np.log(d["current_ratio"].clip(lower=0.1)), "max")

    # Cashflow : marge FCF + cash conversion
    s_cash = 0.6 * _score_rang(d["marge_fcf"], "max") + 0.4 * _score_rang(d["cash_conversion"], "max")

    # Extra-financier : intensité carbone (min), part CA vert (max), score ESG (max)
    s_extra = (
        0.5 * _score_rang(d["intensite_carbone"], "min")
        + 0.25 * _score_rang(d["part_ca_vert"], "max")
        + 0.25 * _score_rang(d["score_esg_global"], "max")
    )

    # ---- Agrégation ----
    w = np.array([
        pond.profitabilite,
        pond.croissance,
        pond.solidite,
        pond.liquidite,
        pond.cashflow,
        pond.extra_financier,
    ], dtype=float)
    w = w / w.sum() if w.sum() > 0 else np.ones_like(w) / len(w)

    score_global = (
        w[0] * s_profit
        + w[1] * s_growth
        + w[2] * s_solid
        + w[3] * s_liq
        + w[4] * s_cash
        + w[5] * s_extra
    )

    out = d[["entreprise", "annee", "secteur"]].copy()
    out["score_global"] = score_global.round(1)

    out["score_profitabilite"] = s_profit.round(1)
    out["score_croissance"] = s_growth.round(1)
    out["score_solidite"] = s_solid.round(1)
    out["score_liquidite"] = s_liq.round(1)
    out["score_cashflow"] = s_cash.round(1)
    out["score_extra_financier"] = s_extra.round(1)

    out = out.sort_values("score_global", ascending=False).reset_index(drop=True)
    return out
