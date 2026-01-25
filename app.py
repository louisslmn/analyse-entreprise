import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "src"))

from donnees import charger_donnees_financieres, charger_donnees_extra_financieres
from ratios import ajouter_ratios, dernier_exercice
from scoring import Ponderations, construire_scores
from visualisation import fig_series, fig_ratios, fig_radar


st.set_page_config(page_title="Analyse entreprise", page_icon="🏢", layout="wide")

st.title("Analyse financière d’entreprise & scoring (avec extra‑financier)")
st.caption(
    "Objectif : démontrer un diagnostic financier (ratios) + un scoring clair, "
    "et introduire une dimension 'finance durable' sans rendre le projet lourd."
)

# ----------------------------
# Chargement des données
# ----------------------------

@st.cache_data
def load_data():
    fin = charger_donnees_financieres(ROOT / "data" / "donnees_financieres.csv")
    extra = charger_donnees_extra_financieres(ROOT / "data" / "donnees_extra_financieres.csv")
    return fin, extra


df_fin, df_extra = load_data()
df_ratios = ajouter_ratios(df_fin)
df_last = dernier_exercice(df_ratios)

entreprises = sorted(df_fin["entreprise"].unique().tolist())

with st.expander("À propos des données", expanded=False):
    st.markdown(
        """
Les données fournies sont des données d’exemple (synthétiques) mais structurées comme un mini‑dataset
de reporting financier (par entreprise/année).

Pourquoi ?
- permettre de tester l’app sans internet
- montrer la méthodologie (ratios, scoring, ranking, visualisations)

Vous pouvez remplacer `data/donnees_financieres.csv` et `data/donnees_extra_financieres.csv` par des données réelles.
        """
    )

# ----------------------------
# Sidebar : pondérations
# ----------------------------
st.sidebar.header("Pondérations du score")

st.sidebar.caption("Astuce : vous pouvez mettre à 0 une famille si vous voulez l'ignorer.")
w_profit = st.sidebar.slider("Profitabilité", 0.0, 3.0, 1.0, 0.1)
w_growth = st.sidebar.slider("Croissance", 0.0, 3.0, 1.0, 0.1)
w_solid = st.sidebar.slider("Solidité (levier)", 0.0, 3.0, 1.0, 0.1)
w_liq = st.sidebar.slider("Liquidité", 0.0, 3.0, 0.7, 0.1)
w_cash = st.sidebar.slider("Cash‑flow", 0.0, 3.0, 1.0, 0.1)
w_extra = st.sidebar.slider("Extra‑financier (carbone/vert/ESG)", 0.0, 3.0, 0.8, 0.1)

pond = Ponderations(
    profitabilite=w_profit,
    croissance=w_growth,
    solidite=w_solid,
    liquidite=w_liq,
    cashflow=w_cash,
    extra_financier=w_extra,
)

scores = construire_scores(df_last, df_extra, pond)

tab_rank, tab_fiche, tab_dl, tab_explain = st.tabs(["Classement", "Fiche entreprise", "Téléchargements", "Explications"])


# ============================
# TAB 1 — Classement
# ============================
with tab_rank:
    st.subheader("Classement (dernier exercice disponible)")

    st.markdown(
        "Le score global agrège des sous‑scores (0..100) via des pondérations choisies dans la sidebar."
    )

    st.dataframe(scores, use_container_width=True)

    topn = st.slider("Afficher le Top N", 3, len(scores), 5, 1)
    st.write(f"Top {topn} :")
    st.table(scores.head(topn)[["entreprise", "secteur", "annee", "score_global"]])


# ============================
# TAB 2 — Fiche entreprise
# ============================
with tab_fiche:
    st.subheader("Fiche entreprise")
    entreprise = st.selectbox("Choisir une entreprise", entreprises)

    col1, col2 = st.columns([0.55, 0.45], gap="large")

    with col1:
        st.pyplot(fig_series(df_fin, entreprise))
        st.pyplot(fig_ratios(df_ratios, entreprise))

    with col2:
        st.markdown("### Dernier exercice — chiffres & ratios")

        last_row = df_last[df_last["entreprise"] == entreprise].iloc[0]
        extra_row = df_extra[df_extra["entreprise"] == entreprise].iloc[0]

        st.write("**Compte de résultat (M€)**")
        st.write(
            {
                "Année": int(last_row["annee"]),
                "CA": float(last_row["chiffre_affaires_m"]),
                "EBIT": float(last_row["ebit_m"]),
                "Résultat net": float(last_row["resultat_net_m"]),
            }
        )

        st.write("**Ratios**")
        st.write(
            {
                "Marge nette": f"{100*last_row['marge_nette']:.1f} %",
                "ROE": f"{100*last_row['roe']:.1f} %",
                "Debt/Equity": f"{last_row['debt_to_equity']:.2f}",
                "Current ratio": f"{last_row['current_ratio']:.2f}",
                "Marge FCF": f"{100*last_row['marge_fcf']:.1f} %",
                "Croissance CA (YoY)": (
                    "n/a" if pd.isna(last_row["croissance_ca"]) else f"{100*last_row['croissance_ca']:.1f} %"
                ),
            }
        )

        st.write("**Extra‑financier** (exemple)")
        st.write(
            {
                "Intensité carbone": f"{extra_row['intensite_carbone']} tCO2e / M€",
                "Part CA vert": f"{100*extra_row['part_ca_vert']:.0f} %",
                "Score ESG global": f"{extra_row['score_esg_global']}/100",
            }
        )

        st.divider()

        st.markdown("### Profil de scores (0..100)")
        s = scores[scores["entreprise"] == entreprise].iloc[0].to_dict()
        radar = {
            "Profit": s["score_profitabilite"],
            "Croissance": s["score_croissance"],
            "Solidité": s["score_solidite"],
            "Liquidité": s["score_liquidite"],
            "Cash": s["score_cashflow"],
            "Extra": s["score_extra_financier"],
        }
        st.pyplot(fig_radar(radar, titre=f"Profil — {entreprise}"))

        st.metric("Score global", f"{s['score_global']:.1f} / 100")


# ============================
# TAB 3 — Téléchargements
# ============================
with tab_dl:
    st.subheader("Exporter")
    st.download_button(
        "⬇️ Télécharger le classement (CSV)",
        data=scores.to_csv(index=False).encode("utf-8"),
        file_name="classement_scores.csv",
        mime="text/csv",
    )
    st.download_button(
        "⬇️ Télécharger les données financières (CSV)",
        data=df_fin.to_csv(index=False).encode("utf-8"),
        file_name="donnees_financieres.csv",
        mime="text/csv",
    )
    st.download_button(
        "⬇️ Télécharger les données extra-financières (CSV)",
        data=df_extra.to_csv(index=False).encode("utf-8"),
        file_name="donnees_extra_financieres.csv",
        mime="text/csv",
    )


# ============================
# TAB 4 — Explications
# ============================
with tab_explain:
    st.subheader("Explications : diagnostic financier + scoring")

    st.markdown(
        """
### 1) Diagnostic financier
On calcule des ratios simples, mais très utilisés :
- Profitabilité : marge, ROE/ROA
- Solidité : dette / capitaux propres
- Liquidité : current ratio
- Cash‑flow : marge FCF, conversion cash (CFO / résultat net)
- Croissance : croissance du chiffre d'affaires

L'idée est d'obtenir une lecture rapide de la santé financière.

### 2) Pourquoi un score ?
Dans un “screener”, on doit comparer plusieurs entreprises.
Plutôt que d'additionner des ratios hétérogènes (unités différentes),
on utilise un score par rang (percentiles) sur 0..100.

- si un ratio doit être grand (ex: marge) → on score en sens “max”
- si un ratio doit être petit (ex: dette/équity) → on score en sens “min”

### 3) Extra-financier (finance durable)
On ajoute une composante légère :
- intensité carbone (plus faible = mieux)
- part de CA “vert”
- score ESG global

Ce n'est pas un modèle ESG institutionnel mais une démonstration de comment intégrer
de l'extra‑financier dans un outil de décision.
        """
    )

    st.markdown(
        """
### 4) Ce que l’application met en œuvre côté Python
- pipeline données (chargement, jointure, transformations)
- calcul vectorisé de ratios (pandas/numpy)
- normalisation robuste (score par rang)
- visualisations (séries + radar)
- interface Streamlit testable
        """
    )
