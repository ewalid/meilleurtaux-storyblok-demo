"""Home personalisation experiment: Contrôle + 3 customer segments, with mock results.

MCP gap: the Storyblok MCP has no experiment operations, so creating the experiment,
its variant stories, activation and results go through the Management API. The variant
stories' content is written through the MCP (updateStory), like every other story.

  python3 07_home_experiment.py create    # experiment + variant stories (copies of home)
  python3 07_home_experiment.py activate  # after the variants are customised and published
  python3 07_home_experiment.py results   # (re)push the mock results dashboard

The frontend serves the variant from cdn/experiments: ?segment=<variant name> forces a
segment (campaign link, CRM audience), otherwise a sticky weighted draw.
"""
import math
import sys

from sb import api

EXP_NAME = "home-segments"
VARIANTS = [
    ("controle", "Contrôle · Accueil actuel", True),
    ("primo-accedants", "Primo-accédants · 1er achat", False),
    ("renegociation", "Propriétaires · Renégociation & rachat", False),
    ("investisseurs", "Investisseurs locatifs", False),
]
LABELS = ["Contrôle", "Primo-accédants", "Renégociation", "Investisseurs"]


def home():
    return api("GET", "/stories?with_slug=home")["stories"][0]


def experiment():
    found = [e for e in api("GET", "/experiments")["experiments"] if e["name"] == EXP_NAME]
    return api("GET", f"/experiments/{found[0]['id']}")["experiment"] if found else None


def create():
    exp = experiment()
    if not exp:
        exp = api("POST", "/experiments", {"experiment": {
            "name": EXP_NAME,
            "display_name": "Accueil · Personnalisation par segment",
            "description": (
                "La page d'accueil adaptée à trois segments clients : primo-accédants (premier achat), "
                "propriétaires qui renégocient ou regroupent leurs crédits, investisseurs locatifs. "
                "Contrôle = accueil actuel. Objectif : démarrage d'une simulation depuis l'accueil."
            ),
            "story_ids": [home()["id"]],
            "experiment_variants_attributes": [
                {"name": n, "display_name": d, "is_control": c, "weight": 25} for n, d, c in VARIANTS
            ],
        }})["experiment"]
    home_id = exp["story_ids"][0]
    for v in exp["experiment_variants"]:
        if v["is_control"] or v.get("story_mappings"):
            continue
        api("POST", f"/experiments/{exp['id']}/variants/{v['id']}/story_mappings",
            {"story_mapping": {"original_story_id": home_id}})
    exp = experiment()
    print("experiment", exp["id"], exp["status"])
    for v in exp["experiment_variants"]:
        for m in v.get("story_mappings") or []:
            print(" ", v["name"], m.get("variant_story_id"), m.get("variant_slug"))


def activate():
    exp = experiment()
    api("GET", f"/stories/{exp['story_ids'][0]}/publish")
    if exp["status"] != "running":
        exp = api("PUT", f"/experiments/{exp['id']}/activate", {})["experiment"]
    print("status", exp["status"], exp["id"])


# Mock data: 21 illustrative days, 4 x 25 % split. Primary goal = a simulation started from
# the home (simulator, capacity calculator or a simulation link).
VISITS = {
    "controle": [612, 598, 640, 587, 655, 702, 571, 618, 631, 604, 596, 668, 583, 627, 615, 601, 644, 590, 661, 695, 578],
    "primo-accedants": [608, 603, 636, 592, 649, 708, 566, 621, 628, 609, 590, 672, 579, 631, 611, 606, 640, 594, 657, 700, 575],
    "renegociation": [615, 595, 642, 584, 651, 699, 574, 612, 634, 600, 599, 665, 586, 622, 618, 598, 647, 586, 664, 691, 581],
    "investisseurs": [606, 601, 638, 590, 653, 704, 569, 616, 629, 606, 593, 670, 581, 629, 613, 603, 642, 592, 659, 697, 576],
}
SIMS = {
    "controle": [37, 35, 39, 34, 40, 44, 33, 37, 38, 36, 35, 41, 34, 38, 37, 35, 39, 35, 40, 43, 34],
    "primo-accedants": [52, 50, 55, 49, 56, 62, 47, 53, 54, 51, 50, 58, 48, 54, 52, 51, 55, 50, 57, 61, 48],
    "renegociation": [47, 44, 49, 43, 50, 55, 42, 46, 48, 45, 45, 51, 44, 47, 47, 44, 49, 44, 51, 54, 43],
    "investisseurs": [41, 40, 43, 39, 44, 49, 37, 41, 42, 40, 39, 45, 38, 42, 41, 40, 43, 39, 44, 48, 38],
}
LEADS_PER_SIM = {"controle": 0.218, "primo-accedants": 0.236, "renegociation": 0.284, "investisseurs": 0.262}
AVG_LOAN = {"controle": 214000, "primo-accedants": 196000, "renegociation": 168000, "investisseurs": 241000}


def pct(a, b, digits=2):
    return round(a / b * 100, digits)


def cum(xs):
    total, out = 0, []
    for x in xs:
        total += x
        out.append(total)
    return out


def z_test(x1, n1, x2, n2):
    p = (x1 + x2) / (n1 + n2)
    z = (x2 / n2 - x1 / n1) / math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return round(z, 2), round(math.erfc(abs(z) / math.sqrt(2)), 4)


def results():
    exp = experiment()
    keys = [n for n, _, _ in VARIANTS]
    n = {k: sum(VISITS[k]) for k in keys}
    s = {k: sum(SIMS[k]) for k in keys}
    rate = {k: pct(s[k], n[k]) for k in keys}
    leads = {k: round(s[k] * LEADS_PER_SIM[k]) for k in keys}
    lead_rate = {k: pct(leads[k], n[k]) for k in keys}
    uplift = {k: round((rate[k] / rate["controle"] - 1) * 100, 1) for k in keys}
    zp = {k: z_test(s["controle"], n["controle"], s[k], n[k]) for k in keys[1:]}
    days = [f"J{d}" for d in range(1, 22)]
    series = lambda values: [{"label": label, "data": values[k]} for label, k in zip(LABELS, keys)]
    by_variant = lambda title, y, values: {
        "kind": "bar", "title": title, "xLabel": "Variante", "yLabel": y, "labels": LABELS,
        "series": [{"label": y, "data": [values[k] for k in keys]}]}

    charts = [
        {"kind": "text", "title": "Synthèse (données fictives)", "body": (
            f"Objectif principal : simulation démarrée depuis l'accueil. "
            f"Contrôle {rate['controle']} %, Primo-accédants {rate['primo-accedants']} % "
            f"({uplift['primo-accedants']:+} %), Renégociation {rate['renegociation']} % "
            f"({uplift['renegociation']:+} %), Investisseurs {rate['investisseurs']} % "
            f"({uplift['investisseurs']:+} %). "
            f"Les trois segments battent le contrôle ; Primo-accédants a l'écart le plus net "
            f"(z = {zp['primo-accedants'][0]}, p = {zp['primo-accedants'][1]}). "
            f"Renégociation convertit le mieux en demande de rappel conseiller. "
            f"{sum(n.values()):,} visites sur 21 jours, répartition 25/25/25/25.".replace(",", " ")
            + " DONNÉES FICTIVES pour la démo : l'expérience et la répartition sont réelles, les chiffres non.")},
        {"kind": "text", "title": "Lecture par segment", "body": (
            "Primo-accédants : bandeau capacité d'emprunt + PTZ, les simulateurs remontés juste sous le bandeau. "
            "Renégociation : bandeau baisse de mensualités, tuile Rachat de crédit mise en avant, offre assurance de prêt (loi Lemoine). "
            "Investisseurs : bandeau investissement locatif, bloc Taux du marché (données BCE) remonté sous le bandeau. "
            "Prochaine étape suggérée : servir chaque variante à son audience (campagne, CRM) plutôt qu'au hasard.")},
        by_variant("Taux de simulation démarrée (objectif principal)", "Simulations / visites (%)", rate),
        by_variant("Demandes de rappel conseiller", "Leads / visites (%)", lead_rate),
        by_variant("Écart vs contrôle sur l'objectif principal", "Uplift (%)", uplift),
        {"kind": "bar", "title": "Parcours après le bandeau (en % des visites)", "xLabel": "Étape",
         "yLabel": "% des visites", "labels": ["Clic bandeau", "Simulation démarrée", "Simulation terminée", "Demande de rappel"],
         "series": [
             {"label": "Contrôle", "data": [14.2, rate["controle"], 3.9, lead_rate["controle"]]},
             {"label": "Primo-accédants", "data": [19.6, rate["primo-accedants"], 5.8, lead_rate["primo-accedants"]]},
             {"label": "Renégociation", "data": [17.9, rate["renegociation"], 5.4, lead_rate["renegociation"]]},
             {"label": "Investisseurs", "data": [16.1, rate["investisseurs"], 4.7, lead_rate["investisseurs"]]},
         ]},
        {"kind": "bar", "title": "Simulateur utilisé (part des simulations)", "xLabel": "Simulateur",
         "yLabel": "Part (%)", "labels": ["Capacité d'emprunt", "Mensualités", "Rachat de crédit", "Assurance de prêt"],
         "series": [
             {"label": "Contrôle", "data": [34, 38, 15, 13]},
             {"label": "Primo-accédants", "data": [57, 31, 4, 8]},
             {"label": "Renégociation", "data": [9, 17, 46, 28]},
             {"label": "Investisseurs", "data": [29, 52, 8, 11]},
         ]},
        {"kind": "bar", "title": "Montant moyen simulé", "xLabel": "Variante", "yLabel": "€",
         "labels": LABELS, "series": [{"label": "Montant moyen (€)", "data": [AVG_LOAN[k] for k in keys]}]},
        {"kind": "bar", "title": "Objectif principal par appareil", "xLabel": "Appareil", "yLabel": "Taux (%)",
         "labels": ["Mobile", "Ordinateur", "Tablette"],
         "series": [
             {"label": "Contrôle", "data": [5.4, 6.9, 5.8]},
             {"label": "Primo-accédants", "data": [8.1, 9.3, 8.4]},
             {"label": "Renégociation", "data": [6.9, 8.4, 7.2]},
             {"label": "Investisseurs", "data": [5.9, 7.9, 6.6]},
         ]},
        {"kind": "bar", "title": "Objectif principal par source de trafic", "xLabel": "Source", "yLabel": "Taux (%)",
         "labels": ["Recherche naturelle", "Recherche payante", "Direct", "Emailing", "Réseaux sociaux"],
         "series": [
             {"label": "Contrôle", "data": [6.1, 6.8, 5.7, 7.2, 4.4]},
             {"label": "Primo-accédants", "data": [8.7, 9.6, 7.9, 9.1, 6.8]},
             {"label": "Renégociation", "data": [7.3, 8.1, 6.5, 9.8, 5.2]},
             {"label": "Investisseurs", "data": [6.6, 7.7, 6.4, 8.3, 4.9]},
         ]},
        {"kind": "bar", "title": "Engagement", "xLabel": "Indicateur", "yLabel": "Valeur",
         "labels": ["Rebond (%)", "Défilement > 50 % (%)", "Temps sur la page (s)"],
         "series": [
             {"label": "Contrôle", "data": [41.8, 46.2, 52]},
             {"label": "Primo-accédants", "data": [34.9, 55.1, 64]},
             {"label": "Renégociation", "data": [36.7, 51.4, 61]},
             {"label": "Investisseurs", "data": [37.9, 53.8, 69]},
         ]},
        by_variant("Contrôle de la répartition du trafic", "Visites", n),
        {"kind": "line", "title": "Taux de simulation cumulé", "xLabel": "Jour", "yLabel": "Cumulé (%)",
         "labels": days, "series": series({k: [pct(a, b) for a, b in zip(cum(SIMS[k]), cum(VISITS[k]))] for k in keys})},
        {"kind": "line", "title": "Taux de simulation par jour", "xLabel": "Jour", "yLabel": "Taux (%)",
         "labels": days, "series": series({k: [pct(a, b) for a, b in zip(SIMS[k], VISITS[k])] for k in keys})},
        {"kind": "line", "title": "Visites par jour", "xLabel": "Jour", "yLabel": "Visites",
         "labels": days, "series": series(VISITS)},
        {"kind": "text", "title": "Avertissement", "body": (
            f"DONNÉES FICTIVES. Expérience {exp['id']}, 4 variantes à 25 %. Les chiffres illustrent "
            "l'écran de résultats alimenté par l'outil d'analytics ; aucun gagnant n'est choisi sur cette base.")},
    ]
    assert len(charts) <= 20
    api("POST", f"/experiments/{exp['id']}/results", {"charts": charts})
    print(f"pushed {len(charts)} charts;", {k: f"{rate[k]}% ({uplift[k]:+}%)" for k in keys})


if __name__ == "__main__":
    {"create": create, "activate": activate, "results": results}[sys.argv[1]]()
