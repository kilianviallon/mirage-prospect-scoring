"""Calcul du score d'une entreprise.

Principe : l'analyste saisit des données observables (avec un statut : fait ou
hypothèse) ; ce module les transforme en notes de 0 à 5 avec les règles de
config/scoring.yaml, puis en score sur 100.
"""

FACT, HYPOTHESIS, UNKNOWN = "fact", "hypothesis", "unknown"
STATUS_RANK = {UNKNOWN: 0, HYPOTHESIS: 1, FACT: 2}


# --------------------------------------------------------------------------- #
# Outils de base
# --------------------------------------------------------------------------- #

def get_field(company, name):
    """Renvoie (valeur, statut, source) d'une donnée. Valeur absente = inconnue."""
    field = company.get(name) or {}
    value = field.get("value")
    if value is None:
        return None, UNKNOWN, None
    status = field.get("status") or HYPOTHESIS  # par prudence : sans statut = hypothèse
    return value, status, field.get("source")


def weakest(statuses):
    """Statut le plus faible d'une liste (fait > hypothèse > inconnu)."""
    return min(statuses, key=lambda s: STATUS_RANK[s]) if statuses else UNKNOWN


def adjust_for_status(note, status, uncertainty):
    """Applique la règle d'incertitude à une note brute."""
    neutral = uncertainty["neutral_score"]
    if status == UNKNOWN:
        return neutral
    if status == HYPOTHESIS:
        # une hypothèse se rapproche de `hypothesis_shift` point(s) du neutre, sans le dépasser
        shift = uncertainty["hypothesis_shift"]
        if note > neutral:
            return max(neutral, note - shift)
        return min(neutral, note + shift)
    return note


# --------------------------------------------------------------------------- #
# Notes brutes, une fonction par type de critère
# Chaque fonction renvoie (note brute ou None si inconnue, statut, explication)
# --------------------------------------------------------------------------- #

def note_categorical(company, crit):
    value, status, _ = get_field(company, crit["field"])
    if value is None:
        return None, UNKNOWN, "donnée inconnue"
    if value not in crit["scores"]:
        raise ValueError(f"Valeur « {value} » non prévue pour {crit['field']}.")
    return crit["scores"][value], status, f"{crit['field']} = {value}"


def note_count_true(company, crit):
    """Compte les cases « oui ». Les cases inconnues ne comptent pas comme « oui »."""
    known = [get_field(company, f) for f in crit["fields"]]
    known = [(f, v, s) for f, (v, s, _) in zip(crit["fields"], known) if v is not None]
    if not known:
        return None, UNKNOWN, "aucune donnée connue"
    count = sum(1 for _, v, _ in known if v is True)
    key = min(count, max(crit["scores"]))
    status = weakest([s for _, v, s in known if v is True] or [s for _, _, s in known])
    yes = [f for f, v, _ in known if v is True]
    return crit["scores"][key], status, f"{count} case(s) cochée(s) : {', '.join(yes) or 'aucune'}"


def note_bands(company, crit):
    value, status, _ = get_field(company, crit["field"])
    if value is None:
        return None, UNKNOWN, "effectif inconnu"
    for low, high, note in crit["bands"]:
        if low <= value <= high:
            return note, status, f"{value} salariés (tranche {low}-{high})"
    return 0, status, f"{value} salariés (hors tranches)"


def note_signals(company, crit):
    """Négatif vérifié > 2 positifs vérifiés > 1 positif vérifié > hypothèses > rien."""
    s = crit["scores"]
    signals = company.get("signals") or []
    neg_facts = [x for x in signals if x.get("negative") and x.get("status") == FACT]
    pos_facts = [x for x in signals if not x.get("negative") and x.get("status") == FACT]
    neg_hyps = [x for x in signals if x.get("negative") and x.get("status") != FACT]
    pos_hyps = [x for x in signals if not x.get("negative") and x.get("status") != FACT]

    if neg_facts:
        return s["negative"], FACT, f"signal négatif vérifié : {neg_facts[0]['description']}"
    if len(pos_facts) >= 2:
        return s["two_or_more_facts"], FACT, f"{len(pos_facts)} signaux vérifiés"
    if len(pos_facts) == 1:
        return s["one_fact"], FACT, f"1 signal vérifié : {pos_facts[0]['description']}"
    if neg_hyps:
        return s["negative"], HYPOTHESIS, f"signal négatif supposé : {neg_hyps[0]['description']}"
    if pos_hyps:
        return s["hypotheses_only"], HYPOTHESIS, f"signal supposé : {pos_hyps[0]['description']}"
    return None, UNKNOWN, "aucun signal trouvé"


NOTE_FUNCTIONS = {
    "categorical": note_categorical,
    "count_true": note_count_true,
    "bands": note_bands,
    "signals": note_signals,
}


# --------------------------------------------------------------------------- #
# Disqualification
# --------------------------------------------------------------------------- #

def check_disqualifiers(company, config):
    """Renvoie (raisons d'exclusion, points à vérifier)."""
    reasons, to_check = [], []
    for rule in config["disqualifiers"]:
        value, status, _ = get_field(company, rule["field"])
        if value is None:
            continue
        hit = (
            ("disqualify_if_in" in rule and value in rule["disqualify_if_in"])
            or ("disqualify_if" in rule and value == rule["disqualify_if"])
            or ("disqualify_if_above" in rule and value > rule["disqualify_if_above"])
            or ("disqualify_if_below" in rule and value < rule["disqualify_if_below"])
        )
        if hit:
            (reasons if status == FACT else to_check).append(rule["reason"])
    return reasons, to_check


# --------------------------------------------------------------------------- #
# Score global
# --------------------------------------------------------------------------- #

def score_company(company, config, weights=None):
    """Calcule le score d'une entreprise.

    `weights` permet de tester d'autres poids sans modifier le fichier de
    configuration (utilisé par les curseurs de l'interface).
    """
    uncertainty = config["uncertainty"]
    weights = weights or {k: c["weight"] for k, c in config["criteria"].items()}
    total_weight = sum(weights.values()) or 1

    details, score, confident_weight = [], 0.0, 0
    for key, crit in config["criteria"].items():
        raw, status, why = NOTE_FUNCTIONS[crit["type"]](company, crit)
        kept = adjust_for_status(raw if raw is not None else 0, status, uncertainty)
        # les poids sont ramenés sur 100 si leur somme a été modifiée
        weight = weights[key] * 100 / total_weight
        points = weight * kept / 5
        score += points
        if status == FACT:
            confident_weight += weight
        details.append({
            "key": key, "label": crit["label"], "weight": round(weight, 1),
            "raw_note": raw, "status": status, "kept_note": round(kept, 2),
            "points": round(points, 1), "why": why,
        })

    reasons, to_check = check_disqualifiers(company, config)
    result = {
        "name": company["name"],
        "sector": company.get("sector"),
        "score": round(score, 1),
        "confidence": round(confident_weight / 100, 2),
        "disqualified": bool(reasons),
        "disqualification_reasons": reasons,
        "to_check": to_check,
        "details": details,
    }
    result["priority"] = priority_label(result, config["priority"])
    return result


def priority_label(result, rules):
    if result["disqualified"]:
        return "Écartée"
    if result["score"] >= rules["high_score"]:
        return "Prioritaire" if result["confidence"] >= rules["min_confidence"] else "À approfondir"
    if result["score"] >= rules["medium_score"]:
        return "Secondaire"
    return "Faible"


def rank(companies, config, weights=None):
    """Classe les entreprises : les écartées en dernier, puis par score décroissant."""
    results = [score_company(c, config, weights) for c in companies]
    return sorted(results, key=lambda r: (r["disqualified"], -r["score"], -r["confidence"]))
