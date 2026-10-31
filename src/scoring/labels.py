"""Libellés en français affichés dans l'interface et les rapports."""

STATUS = {"fact": "Fait vérifié", "hypothesis": "Hypothèse", "unknown": "Inconnu"}

CHOICES = {
    "business_model": {
        "commissionnaire": "Commissionnaire de transport",
        "transitaire": "Transitaire",
        "entreprise_generale": "Entreprise générale (BTP)",
        "sous_traitant_industriel": "Sous-traitant industriel",
        "distributeur_b2b": "Distributeur B2B",
        "agence_evenementielle": "Agence événementielle",
        "transporteur_flotte_propre": "Transporteur avec sa propre flotte",
        "autre": "Autre",
    },
    "volume_level": {
        "eleve": "Élevé (> 100 offres/an ou > 1 000 commandes/an)",
        "moyen": "Moyen (30 à 100 offres/an)",
        "faible": "Faible (< 30 offres/an)",
    },
    "case_match": {
        "same_business": "Même métier qu'un client Mirage",
        "same_mechanism": "Même mécanique, secteur voisin",
        "analogy": "Simple analogie",
        "none": "Aucun lien",
    },
    "software_status": {
        "known_with_api": "Connu, avec API",
        "known": "Connu (API non vérifiée)",
    },
    "legal_status": {
        "active": "En activité",
        "procedure_collective": "Procédure collective",
        "liquidation": "Liquidation",
    },
}

BOOLEAN_FIELDS = {
    "free_text_requests": "Demandes reçues en texte libre",
    "email_or_pdf_orders": "Demandes ou commandes par e-mail / PDF",
    "drawings_to_read": "Plans à lire pour chiffrer",
    "decision_center_outside_zone": "Centre de décision hors de la zone (rachat par un groupe extérieur)",
    "competitor_covers_core_workflow": "Outil concurrent couvrant déjà le workflow principal",
}

# Types de signaux de timing : (libellé, signal négatif ?)
SIGNAL_TYPES = {
    "croissance": ("Croissance forte de l'activité", False),
    "recrutement": ("Recrutements sur le workflow visé", False),
    "rachat_direction": ("Rachat ou nouvelle direction", False),
    "gros_contrat": ("Gros contrat ou marché remporté", False),
    "expansion": ("Expansion (nouveaux pays, nouveaux sites)", False),
    "changement_logiciel": ("Changement ou mise à jour du logiciel (TMS, ERP)", False),
    "promesse_delai": ("Promesse publique de délai de réponse", False),
    "autre_positif": ("Autre signal positif", False),
    "baisse_activite": ("Baisse d'activité ou licenciements", True),
    "litige": ("Litige ou conflit entre actionnaires", True),
    "difficultes_financieres": ("Difficultés financières", True),
    "autre_negatif": ("Autre signal négatif", True),
}

SIGNAL_YEARS = ["2026", "2025", "2024", "Avant 2024"]

SECTORS = ["transport", "btp", "industrie", "evenementiel", "distribution", "autre"]

PRIORITY_COLORS = {
    "Prioritaire": "🟢", "À approfondir": "🟡", "Secondaire": "🔵",
    "Faible": "⚪", "Écartée": "🔴",
}
