# Méthodologie du scoring

Ce document explique comment l'outil classe les entreprises selon leur potentiel commercial pour Mirage Metrics. Toutes les valeurs citées (poids, seuils, barèmes) se trouvent dans `config/scoring.yaml` et peuvent être modifiées sans toucher au code.

Le principe général, un exemple de calcul et les limites de l'outil sont présentés dans le README du projet. Cette page détaille les règles de calcul.

## 1. Critères de disqualification

| Règle | Justification |
|---|---|
| Procédure collective ou liquidation | Pas de budget, avenir de l'entreprise incertain |
| Centre de décision hors de la zone ciblée (rachat par un groupe étranger) | Le choix des outils se fait au siège, hors de portée de la prospection locale |
| Plus de 5 000 salariés | Un très grand groupe relève d'une approche grands comptes (plusieurs décideurs, appels d'offres, cycle de plusieurs mois), pas de cette prospection ciblée |
| Outil concurrent couvrant déjà le workflow principal | Pas de besoin à vendre |

Il n'y a **pas de seuil minimal de taille** : une petite entreprise peut avoir besoin de ce type d'agent, et l'implémentation y est souvent plus simple (un seul décideur, des processus moins nombreux). Son budget et son volume plus limités sont pris en compte par les critères de taille et de volume, sans l'exclure.

Le seuil de 5 000 salariés laisse dans le périmètre des entreprises comparables aux clients actuels de Mirage, qui vont de la PME (Transwin, OFRET) à l'entreprise de plus de 1 000 salariés (OCBM). Les très grands groupes restent un marché pour Mirage (John Cockerill est client via sa filiale marocaine), mais avec une autre méthode commerciale.

Si une condition de disqualification n'est qu'une **hypothèse**, l'entreprise n'est pas écartée : elle est signalée « à vérifier ».

## 2. Critères de qualification

Les sept critères répondent à trois questions qu'un commercial se pose.

### A. A-t-elle le problème que Mirage résout ? (50 points)

| Critère | Poids | Justification |
|---|---|---|
| Rôle d'intermédiaire | 25 | C'est le cœur du profil cible : une entreprise qui fait le lien entre un client et des prestataires, comme OFRET avec son réseau de transporteurs. |
| Volume de demandes | 10 | Plus il y a de demandes, plus le gain est grand. Poids limité car cette donnée est rarement vérifiable de l'extérieur. |
| Demandes non structurées | 15 | L'agent apporte le plus de valeur quand les demandes arrivent en texte libre, en PDF ou sous forme de plans. |

### B. Mirage peut-il gagner ce client ? (25 points)

| Critère | Poids | Justification |
|---|---|---|
| Proximité avec un cas Mirage | 15 | Un cas client du même métier est la meilleure preuve à présenter à un prospect. |
| Logiciel intégrable | 10 | Le gain dépend du branchement direct sur le logiciel du client (le TMS chez OFRET). Poids modéré : Mirage s'intègre aux outils existants, et ce point se confirme souvent au premier rendez-vous. |

### C. Peut-elle acheter maintenant ? (25 points)

| Critère | Poids | Justification |
|---|---|---|
| Taille et budget | 10 | Entre 20 et 500 salariés, le budget existe et la décision est rapide. Les petites structures restent intéressantes (implémentation simple) mais ont moins de budget. |
| Signal de timing | 15 | Une entreprise qui a une raison d'agir maintenant (croissance, rachat, recrutements sur le workflow visé) est plus facile à convaincre. |

### Barèmes de notation

| Critère | Donnée utilisée | Note |
|---|---|---|
| Rôle d'intermédiaire | Type d'activité | commissionnaire 5 ; transitaire, entreprise générale 4 ; sous-traitant industriel, distributeur B2B, agence événementielle 3 ; transporteur avec sa propre flotte 1 ; autre 0 |
| Volume de demandes | Niveau estimé | élevé 5 ; moyen 3 ; faible 1 |
| Demandes non structurées | Formulaire en texte libre / commandes par e-mail ou PDF / plans à lire | 2 ou plus 5 ; 1 3 ; aucun 1 |
| Proximité avec un cas Mirage | Lien avec un cas client | même métier 5 ; même mécanique dans un secteur voisin 3 ; analogie 1 ; aucun 0 |
| Logiciel intégrable | Statut du logiciel | connu avec API 5 ; connu 3 ; inconnu : note neutre |
| Taille et budget | Nombre de salariés | 20-500 : 5 ; 1-19 ou 501-2 000 : 3 ; 2 001-5 000 : 1 ; plus de 5 000 : disqualifiée |
| Signal de timing | Signaux sourcés | signal négatif vérifié 0 (l'emporte sur tout signal positif) ; 2 signaux vérifiés ou plus 5 ; 1 signal vérifié 4 ; signaux seulement supposés 4, ramené à 3 par la règle des hypothèses ; aucun signal trouvé : note neutre |

## 3. Données manquantes et incertitudes

Chaque donnée porte un statut :

| Statut | Traitement |
|---|---|
| **Fait** (vérifié, avec source) | La note compte entièrement. |
| **Hypothèse** | La note se rapproche de **1 point** de la note neutre (2,5), sans la dépasser : 5 → 4, 4 → 3, 3 → 2,5, 1 → 2, 0 → 1. Une hypothèse favorable est revue à la baisse, une hypothèse défavorable à la hausse : le doute joue dans les deux sens. |
| **Inconnu** | La note vaut la note neutre, **2,5 sur 5**. On ne récompense pas ce qu'on ignore, sans éliminer l'entreprise pour autant. |

Pour le critère « Demandes non structurées », qui combine trois cases (texte libre, e-mail ou PDF, plans) : une case inconnue ne compte pas comme cochée, et le critère prend le statut le plus faible des cases cochées. Si les trois cases sont inconnues, la note neutre s'applique.

L'**indice de confiance** est la somme des poids des critères dont le statut est « fait », divisée par 100. Il indique la part du score qui repose sur des informations vérifiées.

## 4. Étiquettes de priorité

| Étiquette | Condition | Action |
|---|---|---|
| **Prioritaire** | Score ≥ 70 et confiance ≥ 50 % | À contacter en premier |
| **À approfondir** | Score ≥ 70 et confiance < 50 % | Bon potentiel, mais trop de données incertaines : recherches complémentaires avant de contacter |
| **Secondaire** | Score entre 50 et 69 | À garder en réserve |
| **Faible** | Score < 50 | Pas prioritaire |
| **Écartée** | Disqualifiée | Ne pas prospecter |
