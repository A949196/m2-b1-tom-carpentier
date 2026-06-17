# M2-B1 — Audit & Pipeline Banque Eckmühl — Tom Carpentier
 
> Audit qualité + éthique du dataset German Credit et industrialisation
> du pipeline de préparation.
 
---

## Reproduire en 3 lignes
 
```bash
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute notebooks/M2-B1_Tom_audit.ipynb
python contract_test.py
```
 
> 📦 Le dataset `german_credit_raw.csv` et le complément `german_credit_supplement.csv`
> sont déjà dans `data/`. Le pipeline persisté `src/pipeline.joblib` est produit
> lors de l'exécution du notebook.
 
---

## Structure du repo
 
```
M2-B1-pipe-eckmuhl-tom/
├── data/
│   ├── german_credit_raw.csv          # dataset source (fourni)
│   ├── german_credit_supplement.csv   # complément customer_segment (tâche 5 bis, fourni)
│   └── german_credit_clean.parquet    # dataset propre (produit, bonus, gitignored)
├── notebooks/
│   └── M2-B1_Tom_audit.ipynb         # livrable principal — audit + pipeline
├── src/
│   ├── preprocess.py                  # Pipeline sklearn + ColumnTransformer
│   └── pipeline.joblib                # pipeline persisté (produit, gitignored)
├── contract_test.py                   # tests de contrat — tous les assert doivent passer
├── audit.md                           # ← verdict qualité + éthique, lisible DPO
├── requirements.txt
└── README.md
```

---

## 📋 Verdict rapide
 
Voir **[audit.md](audit.md)** pour le verdict complet destiné au DPO Klaus Eichmann.
 
| Signal | Chiffre clé |
|---|---|
| Valeurs atypiques `credit_amount` | 72 outliers IQR |
| Déséquilibre `foreign_worker` | 963 yes vs 37 no (96,3 % / 3,7 %) |
| Déséquilibre cible | 70 % bon crédit / 30 % mauvais crédit |
| DI `foreign_worker` | **0,777** ⚠️ signal (< 0,80) |
| DI `sex_binary` | 0,896 ✅ pas de signal |
 
---