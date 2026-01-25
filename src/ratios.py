"""
ratios.py
=========

Calcul de ratios financiers courants (sans complexité inutile).

Hypothèse : les montants sont en "millions" (peu importe l'unité tant que c'est cohérent).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def ajouter_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute des ratios au DataFrame (par entreprise/année).

    Ratios calculés :
    - marge nette
    - marge EBIT
    - ROA / ROE
    - debt-to-equity
    - current ratio
    - FCF (free cash flow) et marge FCF
    - cash conversion (CFO / résultat net)
    - croissance CA (YoY)
    """
    d = df.copy()

    d["marge_ebit"] = d["ebit_m"] / d["chiffre_affaires_m"]
    d["marge_nette"] = d["resultat_net_m"] / d["chiffre_affaires_m"]

    d["roa"] = d["resultat_net_m"] / d["actifs_totaux_m"]
    d["roe"] = d["resultat_net_m"] / d["capitaux_propres_m"]

    d["debt_to_equity"] = d["dette_totale_m"] / d["capitaux_propres_m"]

    d["current_ratio"] = d["actifs_courants_m"] / d["passifs_courants_m"]

    d["fcf_m"] = d["flux_tresorerie_op_m"] - d["capex_m"]
    d["marge_fcf"] = d["fcf_m"] / d["chiffre_affaires_m"]

    # cash conversion : attention si résultat net proche de 0
    d["cash_conversion"] = d["flux_tresorerie_op_m"] / d["resultat_net_m"].replace(0, np.nan)

    # croissance YoY par entreprise
    d["croissance_ca"] = (
        d.sort_values(["entreprise", "annee"])
         .groupby("entreprise")["chiffre_affaires_m"]
         .pct_change()
    )

    return d


def dernier_exercice(df_ratios: pd.DataFrame) -> pd.DataFrame:
    """
    Extrait le dernier exercice disponible pour chaque entreprise.
    """
    idx = df_ratios.groupby("entreprise")["annee"].idxmax()
    return df_ratios.loc[idx].reset_index(drop=True)
