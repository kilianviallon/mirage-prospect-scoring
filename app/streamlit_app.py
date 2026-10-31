"""Interface du moteur de prospection Mirage Metrics.

Lancement : streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scoring.engine import rank, score_company  # noqa: E402
from scoring.explain import explain  # noqa: E402
from scoring.labels import BOOLEAN_FIELDS, CHOICES, PRIORITY_COLORS, SECTORS, STATUS  # noqa: E402
from scoring.loader import append_company, load_companies, load_config  # noqa: E402

UNKNOWN = "— Inconnu —"
STATUS_OPTIONS = {"Fait vérifié": "fact", "Hypothèse": "hypothesis"}

st.set_page_config(page_title="Mirage Prospect Scoring", page_icon="🎯", layout="wide")
config = load_config()
criteria = config["criteria"]


# --------------------------------------------------------------------------- #
# Barre latérale : poids modifiables (test en direct, sans toucher au fichier)
# --------------------------------------------------------------------------- #

def reset_weights():
    for key, crit in criteria.items():
        st.session_state[f"w_{key}"] = crit["weight"]


with st.sidebar:
    st.header("⚖️ Poids des critères")
    st.caption("Modifiez les poids pour tester leur effet sur le classement. "
               "Ils sont ramenés sur 100 automatiquement ; le fichier de configuration n'est pas modifié.")
    weights = {}
    for key, crit in criteria.items():
        weights[key] = st.slider(crit["label"], 0, 50, crit["weight"], step=5, key=f"w_{key}",
                                 help=crit["question"])
    total = sum(weights.values())
    st.metric("Somme des poids", total, delta=None if total == 100 else f"{total - 100:+d} (ramené sur 100)")
    st.button("Revenir aux poids d'origine", on_click=reset_weights)

st.title("🎯 Moteur de prospection Mirage Metrics")
tab_rank, tab_add, tab_method = st.tabs(["📊 Classement", "➕ Ajouter une entreprise", "📘 Méthode"])


# --------------------------------------------------------------------------- #
# Onglet 1 : classement
# --------------------------------------------------------------------------- #

with tab_rank:
    companies = load_companies()
    results = rank(companies, config, weights)

    rows = []
    for i, r in enumerate(results, start=1):
        rows.append({
            "Rang": str(i) if not r["disqualified"] else "—",
            "Entreprise": r["name"],
            "Secteur": r["sector"],
            "Score": r["score"],
            "Confiance": f"{int(r['confidence'] * 100)} %",
            "Priorité": f"{PRIORITY_COLORS[r['priority']]} {r['priority']}",
        })
    table = pd.DataFrame(rows)

    c1, c2, c3 = st.columns(3)
    c1.metric("Entreprises analysées", len(results))
    c2.metric("Prioritaires", sum(r["priority"] == "Prioritaire" for r in results))
    c3.metric("Écartées", sum(r["disqualified"] for r in results))

    st.dataframe(
        table, hide_index=True, width="stretch",
        column_config={"Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.1f")},
    )
    st.download_button("⬇️ Télécharger le classement (CSV)", table.to_csv(index=False).encode("utf-8"),
                       "classement.csv", "text/csv")

    st.subheader("🔍 Explication du score")
    chosen = st.selectbox("Entreprise", [r["name"] for r in results])
    result = next(r for r in results if r["name"] == chosen)
    company = next(c for c in companies if c["name"] == chosen)
    st.markdown(explain(result))

    detail = pd.DataFrame([{
        "Critère": d["label"], "Poids": d["weight"], "Donnée": d["why"],
        "Statut": STATUS[d["status"]], "Note brute": d["raw_note"],
        "Note retenue": d["kept_note"], "Points": d["points"],
    } for d in result["details"]])
    st.dataframe(detail, hide_index=True, width="stretch")

    with st.expander("Sources et notes"):
        if company.get("website"):
            st.markdown(f"Site : {company['website']}")
        st.markdown(f"Cas Mirage de référence : {company.get('reference_case', '—')}")
        if company.get("notes"):
            st.markdown(f"Notes : {company['notes']}")
        sources = sorted({v.get("source") for v in company.values()
                          if isinstance(v, dict) and v.get("source")}
                         | {s.get("source") for s in company.get("signals") or [] if s.get("source")})
        for s in sources:
            st.markdown(f"- {s}")


# --------------------------------------------------------------------------- #
# Onglet 2 : ajout d'une entreprise
# --------------------------------------------------------------------------- #

def field_inputs(field, label, choices, help_text=None):
    """Une ligne de saisie : valeur (menu déroulant), statut, source."""
    c1, c2, c3 = st.columns([3, 1.3, 3])
    options = [UNKNOWN] + list(choices.values())
    picked = c1.selectbox(label, options, key=f"v_{field}", help=help_text)
    status = c2.selectbox("Statut", list(STATUS_OPTIONS), key=f"s_{field}")
    source = c3.text_input("Source (URL)", key=f"src_{field}")
    if picked == UNKNOWN:
        return {"value": None, "status": None, "source": None}
    value = next(k for k, v in choices.items() if v == picked)
    return {"value": value, "status": STATUS_OPTIONS[status], "source": source or None}


YES_NO = {True: "Oui", False: "Non"}

with tab_add:
    st.caption("Choisissez pour chaque critère la valeur observée, son statut (fait vérifié ou hypothèse) "
               "et sa source. Laissez « Inconnu » si l'information n'est pas disponible : "
               "la note neutre de 2,5/5 sera appliquée.")

    with st.form("new_company"):
        st.subheader("1. Identité")
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Nom de l'entreprise *")
        website = c2.text_input("Site web")
        city = c3.text_input("Ville")
        c1, c2 = st.columns(2)
        sector = c1.selectbox("Secteur", SECTORS)
        reference_case = c2.text_input("Cas Mirage de référence", placeholder="ex. OFRET / SWILL")
        notes = st.text_area("Notes", height=70)

        st.subheader("2. Critères de disqualification")
        legal = field_inputs("legal_status", "Situation juridique", CHOICES["legal_status"])
        outside = field_inputs("decision_center_outside_zone",
                               BOOLEAN_FIELDS["decision_center_outside_zone"], YES_NO)
        competitor = field_inputs("competitor_covers_core_workflow",
                                  BOOLEAN_FIELDS["competitor_covers_core_workflow"], YES_NO)

        st.subheader("3. Critères de qualification")
        business = field_inputs("business_model", criteria["intermediary_role"]["label"],
                                CHOICES["business_model"], criteria["intermediary_role"]["question"])
        volume = field_inputs("volume_level", criteria["request_volume"]["label"],
                              CHOICES["volume_level"], criteria["request_volume"]["question"])
        st.markdown(f"**{criteria['unstructured_inputs']['label']}**")
        free_text = field_inputs("free_text_requests", BOOLEAN_FIELDS["free_text_requests"], YES_NO)
        email_pdf = field_inputs("email_or_pdf_orders", BOOLEAN_FIELDS["email_or_pdf_orders"], YES_NO)
        drawings = field_inputs("drawings_to_read", BOOLEAN_FIELDS["drawings_to_read"], YES_NO)
        case = field_inputs("case_match", criteria["mirage_case_proximity"]["label"],
                            CHOICES["case_match"], criteria["mirage_case_proximity"]["question"])
        software = field_inputs("software_status", criteria["integrable_software"]["label"],
                                CHOICES["software_status"], criteria["integrable_software"]["question"])
        software["name"] = st.text_input("Nom du logiciel (si connu)", key="software_name") or None

        st.markdown(f"**{criteria['size']['label']}**")
        c1, c2, c3 = st.columns([3, 1.3, 3])
        employees_value = c1.number_input("Nombre de salariés (vide = inconnu)", min_value=1, step=1,
                                          value=None, key="v_employees")
        employees_status = c2.selectbox("Statut", list(STATUS_OPTIONS), key="s_employees")
        employees_source = c3.text_input("Source (URL)", key="src_employees")

        st.markdown(f"**{criteria['timing']['label']}** (jusqu'à 3 signaux, laisser vide si aucun)")
        signals = []
        for i in range(3):
            c1, c2, c3, c4 = st.columns([3, 1.3, 1, 2.7])
            desc = c1.text_input(f"Signal {i + 1}", key=f"sig_d_{i}",
                                 placeholder="ex. croissance de 15 %, rachat, recrutements…")
            sig_status = c2.selectbox("Statut", list(STATUS_OPTIONS), key=f"sig_s_{i}")
            negative = c3.selectbox("Effet", ["Positif", "Négatif"], key=f"sig_n_{i}")
            sig_source = c4.text_input("Source (URL)", key=f"sig_src_{i}")
            if desc.strip():
                signals.append({"description": desc.strip(), "status": STATUS_OPTIONS[sig_status],
                                "source": sig_source or None, "negative": negative == "Négatif"})

        b1, b2 = st.columns(2)
        compute = b1.form_submit_button("🧮 Calculer le score", width="stretch")
        save = b2.form_submit_button("💾 Calculer et enregistrer", type="primary", width="stretch")

    if compute or save:
        company = {
            "name": name.strip(), "website": website or None, "sector": sector, "city": city or None,
            "reference_case": reference_case or None, "notes": notes or None,
            "legal_status": legal, "decision_center_outside_zone": outside,
            "competitor_covers_core_workflow": competitor,
            "business_model": business, "volume_level": volume,
            "free_text_requests": free_text, "email_or_pdf_orders": email_pdf, "drawings_to_read": drawings,
            "case_match": case, "software_status": software,
            "employees": {"value": int(employees_value) if employees_value else None,
                          "status": STATUS_OPTIONS[employees_status] if employees_value else None,
                          "source": employees_source or None},
            "signals": signals,
        }
        if not company["name"]:
            st.error("Indiquez au moins le nom de l'entreprise.")
        else:
            result = score_company(company, config, weights)
            c1, c2, c3 = st.columns(3)
            c1.metric("Score", f"{result['score']} / 100")
            c2.metric("Confiance", f"{int(result['confidence'] * 100)} %")
            c3.metric("Priorité", f"{PRIORITY_COLORS[result['priority']]} {result['priority']}")
            st.markdown(explain(result))
            st.dataframe(pd.DataFrame([{
                "Critère": d["label"], "Donnée": d["why"], "Statut": STATUS[d["status"]],
                "Note retenue": d["kept_note"], "Points": d["points"],
            } for d in result["details"]]), hide_index=True, width="stretch")
            if save:
                try:
                    append_company(company)
                    st.success(f"« {company['name']} » a été ajoutée à data/companies.yaml. "
                               "Elle apparaît dans l'onglet Classement.")
                except ValueError as e:
                    st.error(str(e))


# --------------------------------------------------------------------------- #
# Onglet 3 : rappel de la méthode
# --------------------------------------------------------------------------- #

with tab_method:
    method = Path(__file__).resolve().parents[1] / "docs" / "methodologie.md"
    st.markdown(method.read_text(encoding="utf-8"))
