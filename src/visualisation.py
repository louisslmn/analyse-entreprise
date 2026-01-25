"""
visualisation.py
================

Graphiques Matplotlib pour l'app Streamlit :
- séries temporelles
- radar (profil de scores)
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def fig_series(df: pd.DataFrame, entreprise: str) -> plt.Figure:
    d = df[df["entreprise"] == entreprise].sort_values("annee")

    fig, ax = plt.subplots()
    ax.plot(d["annee"], d["chiffre_affaires_m"], marker="o", label="CA")
    ax.plot(d["annee"], d["ebit_m"], marker="o", label="EBIT")
    ax.plot(d["annee"], d["resultat_net_m"], marker="o", label="Résultat net")
    ax.set_title(f"Compte de résultat — {entreprise}")
    ax.set_xlabel("Année")
    ax.set_ylabel("M€")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def fig_ratios(df_ratios: pd.DataFrame, entreprise: str) -> plt.Figure:
    d = df_ratios[df_ratios["entreprise"] == entreprise].sort_values("annee")

    fig, ax = plt.subplots()
    ax.plot(d["annee"], 100*d["marge_nette"], marker="o", label="Marge nette (%)")
    ax.plot(d["annee"], 100*d["marge_ebit"], marker="o", label="Marge EBIT (%)")
    ax.plot(d["annee"], 100*d["roe"], marker="o", label="ROE (%)")
    ax.set_title(f"Ratios clés — {entreprise}")
    ax.set_xlabel("Année")
    ax.set_ylabel("%")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def fig_radar(scores: dict, titre: str = "Profil de scores") -> plt.Figure:
    """
    Radar chart simple.
    scores : dict {nom: valeur 0..100}
    """
    labels = list(scores.keys())
    values = np.array(list(scores.values()), dtype=float)

    # fermer le polygone
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    values = np.concatenate([values, values[:1]])
    angles = np.concatenate([angles, angles[:1]])

    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])
    ax.set_title(titre)
    fig.tight_layout()
    return fig
