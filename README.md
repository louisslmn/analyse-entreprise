# Analyse d’entreprise : ratios & scoring 

Cette application est un mini “screener” :
- calcul de ratios financiers par entreprise,
- score global paramétrable (pondérations ajustables),
- ajout d’une dimension extra‑financière (exemple) pour enrichir la lecture,
- fiche entreprise + graphiques + radar des scores.

---

## Lancer l’application

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Données

Les fichiers fournis dans `data/` sont des données d’exemple (synthétiques), uniquement pour pouvoir lancer l’application immédiatement :

- `data/donnees_financieres.csv` : dataset financier
- `data/donnees_extra_financieres.csv` : dataset extra‑financier

Vous pouvez remplacer ces CSV par vos propres données si vous respectez la même structure de colonnes (ou en adaptant légèrement `src/donnees.py`).

---

## Structure

- `src/donnees.py` : chargement + jointure des datasets
- `src/ratios.py` : calcul des ratios
- `src/scoring.py` : normalisation (rang/percentile) + score global
- `src/visualisation.py` : séries + radar chart
- `app.py` : interface Streamlit

