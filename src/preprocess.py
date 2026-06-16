"""M2-B1 — Pipeline de préparation pour le scoring crédit Eckmühl.

À compléter par toi pendant le brief. Le squelette pose les bonnes briques
scikit-learn (ColumnTransformer + Pipeline) mais les listes de features et
les choix d'encodage sont des TODO — c'est ce que ton audit qualité va
trancher.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

# ---------------------------------------------------------------------------
# TODO 1 — Remplir les 3 listes de features à partir de ton EDA
# ---------------------------------------------------------------------------
# Une feature peut être :
#   • Numérique continue          → NUMERIC_FEATURES
#   • Catégorielle ordonnée       → ORDINAL_FEATURES (modalités à ordonner)
#   • Catégorielle non ordonnée   → CATEGORICAL_FEATURES (faible cardinalité)
#
# Décide en regardant le notebook (distribution, sens métier).
# Tu peux exclure des features (ex. variable sensible évidente) — argumente
# ce choix dans ton notebook ET ton audit.md.

NUMERIC_FEATURES: list[str] = [
    # ex. "duration_months", "credit_amount", "age", ...
    "duration_months", "credit_amount", "installment_rate_pct_income", "residence_since_years", "age", "n_existing_credits", "n_people_liable"    
]
ORDINAL_FEATURES: dict[str, list[str]] = {
    # ex. "savings_account": ["< 100 DM", "100-500 DM", "500-1000 DM",
    #                         ">= 1000 DM", "unknown / no savings"],
    # Note : l'ordre des modalités encode la sémantique.
    "checking_account_status": [
        "<0 DM", 
        "0 to 200 DM", 
        ">= 200 DM / salary assignment for at least 1 year", 
        "no checking account",
    ], 
    "credit_history": [
        "critical account / other credits existing",
        "delay in paying off in the past", 
        "existing credits paid back duly till now", 
        "existing credits paid back duly", 
        "all credits at this bank paid back duly",
        "no credits taken / all credits paid back duly",
    ], 
    "savings_account": [
        "unknown / no savings",
        "< 100 DM",
        "100 to 500 DM",
        "500 to 1000 DM",
        ">= 1000 DM",    
    ], 
    "employment_since": [
        "unemployed",
        "< 1 year",
        "1-4 years",
        "4-7 years",
        ">= 7 years",
    ], 
    "other_debtors": [
        "co-applicant",
        "guarantor",
        "none",
    ], 
    "property": [
        "unknown / no property",
        "car or other",
        "building society savings agreement / life insurance",
        "real estate",
    ]
}
CATEGORICAL_FEATURES: list[str] = [
    # ex. "purpose", "housing", "telephone", ...
    "purpose", "personal_status_sex", "other_installment_plans", "housing", "job", "telephone", "foreign_worker"
]
TARGET_COLUMN: str = "credit_risk"
TARGET_MAPPING: dict[str, int] = {"good_credit": 0, "bad_credit": 1}


def load_dataset(path: Path, supplement_path: Path | None = None) -> tuple[pd.DataFrame, pd.Series]:
    """Charge le CSV German Credit et retourne (X, y).

    Les features sont sélectionnées d'après les 3 listes définies ci-dessus.
    Les colonnes du CSV qui ne sont dans aucune liste sont **droppées**
    — sois explicite sur tes choix.
    """
    df = pd.read_csv(path)
    
    if supplement_path is not None and supplement_path.exists():
        supplement = pd.read_csv(supplement_path)
        if len(supplement) != len(df):
            raise ValueError(
                f"Supplement ({len(supplement)} lignes) ne correspond pas au dataset principal ({len(df)} lignes)"
            )
        df = pd.concat(
            [df.reset_index(drop=True), supplement.rest_index(drop=True)],
            axis=1,
        )

    y = df[TARGET_COLUMN].map(TARGET_MAPPING)
    if y.isna().any():
        unknown = df.loc[y.isna(), TARGET_COLUMN].unique().tolist()
        raise ValueError(f"Cible non mappée : {unknown}")
    all_features = NUMERIC_FEATURES + list(ORDINAL_FEATURES) + CATEGORICAL_FEATURES
    missing = [c for c in all_features if c not in df.columns]
    if missing:
        raise KeyError(f"Colonnes attendues absentes du CSV : {missing}")
    X = df[all_features].copy()
    return X, y


def build_preprocessor(with_supplement: bool = False) -> Pipeline:
    """Construit le ColumnTransformer.

    3 branches :
      • num : imputation médiane + scaling
      • ord : imputation modale + ordinal encoding (ordre défini par dict)
      • cat : imputation modale + one-hot
    """
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    ordinal_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "ordinal",
                OrdinalEncoder(
                    categories=[ORDINAL_FEATURES[c] for c in ORDINAL_FEATURES],
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                ),
            ),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    transformers = [
        ("num", numeric_pipeline, NUMERIC_FEATURES),
        ("ord", ordinal_pipeline, list(ORDINAL_FEATURES)),
        ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
    ]
    
    col_transformer = ColumnTransformer(
        transformers = transformers,
        remainder="drop",
        verbose_feature_names_out=False
    )

    return Pipeline(steps=[("preprocessor", col_transformer)])


def fit_and_save(data_path: Path, output_path: Path) -> None:
    """Fit le pipeline sur tout le dataset et sauve avec joblib.

    Note : on fit ici sur tout le dataset (pas de split) car en M2-B1
    on produit le **pipeline de préparation**, pas un modèle de scoring.
    Le pipeline sera rejoué tel quel sur tout nouveau lot de données.
    """
    X, _y = load_dataset(data_path)
    pipeline = build_preprocessor()
    pipeline.fit(X)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_path, compress=3)
    print(f"Pipeline saved → {output_path}")


if __name__ == "__main__":
    fit_and_save(
        data_path=Path("data/german_credit_raw.csv"),
        output_path=Path("src/pipeline.joblib"),
    )
