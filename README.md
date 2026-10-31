# Outil de scoring Mirage Metrics

## Description

Nous avons implémenté dans ce projet un outil de scoring d'entreprises permettant de :

- Calculer un score de manière reproductible.
- Gérer des **données manquantes** et des **incertitudes**.
- Produire un **classement des entreprises** accompagné d'une explication des scores.
- Afficher sur une **interface** les scores calculés à partir de nos critères.
- Ajouter de nouvelles entreprises à l'outil de scoring.

Le scoring repose sur des **critères de qualification** pertinents et justifiés, et sur un système de pondération explicite. Des **critères de disqualification** sont aussi implémentés.

## Installation et lancement

**Prérequis :** Python 3.10 ou plus récent.

### 1. Récupérer le projet

```bash
git clone https://github.com/kilianviallon/mirage-prospect-scoring.git
cd mirage-prospect-scoring
```

### 2. Créer et activer un environnement virtuel

L'environnement virtuel isole les bibliothèques du projet du reste de l'ordinateur. Il n'est à créer qu'une seule fois.

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

### 4. Lancer l'interface

```bash
python -m streamlit run app/streamlit_app.py
```

L'interface s'ouvre dans le navigateur à l'adresse `http://localhost:8501`. Au premier lancement, Streamlit demande une adresse e-mail : laisser le champ vide et appuyer sur Entrée. Pour arrêter l'application : `Ctrl+C` dans le terminal.

### Lancer les tests

```bash
python -m pytest
```

## 1. Principe général

L'outil sépare **ce qu'on observe** de **ce qu'on en conclut** :

- l'analyste saisit des **données observables** sur chaque entreprise (type d'activité, effectif, format des demandes, logiciel utilisé, signaux récents), chacune avec sa **source** et son **statut** ;
- l'outil **calcule les notes** à partir de ces données en appliquant des règles fixes.

Le calcul se fait en trois étapes :

1. **Disqualification** : on écarte les entreprises qui ne doivent pas être prospectées.
2. **Score sur 100** : sept critères notés de 0 à 5, multipliés par leur poids.
3. **Indice de confiance** : la part du score qui repose sur des faits vérifiés (prise en compte des données manquantes).

## 2. Présentation de l'interface

Lorsque vous arrivez sur l'application, vous trouverez :

- un espace pour modifier le poids des critères (à gauche de l'écran) ;
- un espace pour ajouter de nouvelles entreprises (onglet *Ajouter une entreprise*) ;
- un espace expliquant le **calcul des notes**, le **barème** et le **choix des critères** (onglet *Méthode*) ;
- un classement récapitulatif de toutes les entreprises, avec l'explication des scores (onglet *Classement*).


## 3. Exemple de calcul (illustratif)

Une entreprise avec les données suivantes :

| Critère | Donnée | Statut | Note | Note retenue | Points |
|---|---|---|---|---|---|
| Rôle d'intermédiaire | commissionnaire | fait | 5 | 5 | 25 × 5/5 = 25,0 |
| Volume de demandes | élevé | hypothèse | 5 | 4,0 | 10 × 4/5 = 8,0 |
| Demandes non structurées | 2 cases cochées | hypothèse | 5 | 4,0 | 15 × 4/5 = 12,0 |
| Proximité avec un cas Mirage | même métier | fait | 5 | 5 | 15 × 5/5 = 15,0 |
| Logiciel intégrable | inconnu | inconnu | — | 2,5 | 10 × 2,5/5 = 5,0 |
| Taille et budget | 35 salariés | hypothèse | 5 | 4,0 | 10 × 4/5 = 8,0 |
| Signal de timing | aucun signal trouvé | inconnu | — | 2,5 | 15 × 2,5/5 = 7,5 |
| **Total** | | | | | **80,5** |

Confiance : seuls le rôle d'intermédiaire (25) et la proximité avec un cas Mirage (15) reposent sur des faits, soit **40 %**.

Résultat : **80,5 points, 40 % de confiance → « À approfondir »**. L'entreprise a un fort potentiel, mais il faut vérifier sa taille, son volume de demandes et son logiciel avant de la contacter.

## 4. Ajouter une nouvelle entreprise

**Avec l'interface (recommandé)** : onglet « Ajouter une entreprise ». Pour chaque critère, choisir la valeur dans le menu déroulant, son statut (fait vérifié ou hypothèse) et sa source, puis cliquer sur « Calculer le score » (aperçu) ou « Calculer et enregistrer » (ajout à `data/companies.yaml`).

**À la main** : copier le modèle `data/company_template.yaml` à la fin de `data/companies.yaml`, remplir chaque donnée, puis relancer l'interface ou le calcul.

## 5. Limites

- Le volume de demandes et le logiciel utilisé sont rarement publics : ces critères reposent souvent sur des hypothèses ou sur la note neutre.
- Les barèmes traduisent un jugement commercial : ils sont explicites et modifiables, mais restent discutables.
- Le traitement des hypothèses (rapprochement de 1 point) et la note neutre (2,5) sont des choix de paramétrage, testables dans l'interface.
