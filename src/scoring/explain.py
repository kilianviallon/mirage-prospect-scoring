"""Explication en français du score d'une entreprise."""

from .labels import STATUS


def explain(result):
    """Résumé lisible : verdict, points forts, points faibles, ce qu'il reste à vérifier."""
    lines = [
        f"**{result['name']}** : {result['score']}/100, "
        f"confiance {int(result['confidence'] * 100)} % → **{result['priority']}**."
    ]
    if result["disqualified"]:
        lines.append("Écartée : " + " ; ".join(result["disqualification_reasons"]) + ".")
        return "\n\n".join(lines)

    strong = [d["label"] for d in result["details"] if d["kept_note"] >= 4]
    weak = [d["label"] for d in result["details"] if d["kept_note"] <= 2]
    uncertain = [
        f"{d['label']} ({STATUS[d['status']].lower()})"
        for d in result["details"] if d["status"] != "fact"
    ]
    if strong:
        lines.append("Points forts : " + ", ".join(strong) + ".")
    if weak:
        lines.append("Points faibles : " + ", ".join(weak) + ".")
    if uncertain:
        lines.append("À confirmer : " + ", ".join(uncertain) + ".")
    if result["to_check"]:
        lines.append("⚠️ Possible exclusion à vérifier : " + " ; ".join(result["to_check"]) + ".")
    return "\n\n".join(lines)
