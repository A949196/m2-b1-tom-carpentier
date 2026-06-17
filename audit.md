# Audit Banque Eckmühl — Pipeline scoring crédit conso

## 1. Verdict qualité

**1. Aucune valeur manquante dans le dataset brut**  
Le dataset ne présente aucune donnée manquante sur les 20 variables et 1 000 dossiers.
Cependant, cela ne garantit pas l'absence d'erreurs de saisie ou d'incohérences de codage.

**2. Valeurs atypiques sur le montant du crédit (`credit_amount`)**  
72 dossiers présentent des montants anormalement élevés.
Ces valeurs extrêmes n'ont pas été supprimées : elles représentent des dossiers réels.

**3. Variable composite `personal_status_sex`**  
Cette variable mélange dans un même champ le genre et le statut marital.
Il est impossible d'isoler l'effet du genre seul, ce qui rend l'audit éthique
sur le genre partiel et difficile à mener.  
Séparer genre et statut civil en deux variables distinctes lors de la prochaine collecte.

**4. Fort déséquilibre sur `foreign_worker`**  
96,3 % des dossiers concernent des résidents non-étrangers (963 dossiers),
contre seulement 3,7 % de résidents étrangers (37 dossiers).
Ce déséquilibre rend les statistiques calculées sur le groupe des étrangers peu fiables.

**5. Déséquilibre modéré de la variable cible**  
70 % des dossiers sont classés « bon crédit », 30 % « mauvais crédit »
(ratio minoritaire/majoritaire : 0,43).
Ce déséquilibre est modéré mais doit être pris en compte lors de l'entraînement
d'un modèle : une règle naïve prédisant toujours « bon crédit » atteindrait
70 % d'exactitude sans rien apprendre des données.

---

## 2. Verdict éthique

Le disparate impact (DI) mesure l'écart de traitement entre deux groupes :  
`DI = taux de crédit favorable (groupe défavorisé) / taux de crédit favorable (groupe de référence)`  
**Seuil réglementaire (règle des 4/5) : DI < 0,80 → signal de biais.**

| Variable sensible | Groupe défavorisé | Taux favorable | DI | Alerte 4/5 | Fiabilité |
|---|---|---|---|---|---|
| `foreign_worker` | Résidents étrangers (`yes`) | 69,3 % | **0,777** | Oui | Effectif faible (37 dossiers) |
| `personal_status_sex` (genre agrégé) | Femmes (`female`) | 64,8 % | 0,896 | Non | Résultat partiel — genre/statut civil mélangés |

**Alerte 1 — `foreign_worker` (DI = 0,777)**  
Les résidents étrangers obtiennent un crédit favorable 22 % moins souvent
que les résidents non-étrangers. Ce signal dépasse le seuil réglementaire des 4/5.
Nuance importante : le groupe des résidents étrangers ne représente que 37 dossiers.

**Alerte 2 — `personal_status_sex` (DI = 0,896)**  
L'analyse agrégée (femmes vs hommes) ne déclenche pas de signal au sens de la règle des 4/5.
Cependant, ce résultat est partiellement non interprétable : la variable mélange
genre et statut civil, ce qui empêche d'isoler l'effet du genre seul.

**Alerte 3 — `customer_segment` (DI = 0.84)**  
Le segment commercial (`basic`, `plus`, `premium`, `private`) corrèle avec
le revenu et le patrimoine du client. Son utilisation dans un modèle de scoring
risque de reproduire mécaniquement des inégalités socio-économiques préexistantes,
même en l'absence de signal DI explicite.

---
## 3. Recommandations

- Corriger la variable composite : séparer `personal_status_sex` en deux variables distinctes (genre et statut civil) et documenter le motif légal
de conservation du genre dans le registre RGPD.

-Élargir la base de données sur `foreign_worker` : avec 37 dossiers, le signal DI est fragile. Collecter davantage de dossiers sur ce groupe.

- Tester `customer_segment` avant intégration : conduire un test de disparate impact spécifique sur cette variable avant de l'inclure dans un modèle de décision crédit.

- Planifier la mitigation*: les biais identifiés ici doivent être traités lors de la phase de correction.


## 4. Limites de cet audit

- Limites statistiques : le groupe des résidents étrangers ne représente que 37 dossiers sur 1 000, l'intervalle de confiance autour de cette valeur est trop large pour tirer des conclusions fiables.
- Limites de mesure : la variable `personal_status_sex` empêche toute analyse propre de l'effet du genre.
- Périmètre de cet audit : ce rapport documente et alerte — il ne corrige pas. A

---

*Audit produit par Tom Carpentier, 16/06/2026, dans le cadre du brief M2-B1 ATOS.*