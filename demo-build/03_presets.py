"""Selectable presets for every Meilleurtaux block (never the default: blank add stays blank) + the component library page.

Presets are taken from the real published pages (first instance of each block),
so picking a preset gives real Meilleurtaux copy and imagery.
The library page shows every section in each of its layouts, built from the
same presets so it never drifts from the schema.

MCP gap: the Storyblok MCP has no preset operations, so this uses the Management API.

Usage: python3 03_presets.py            # presets only
       python3 03_presets.py --library  # presets + (re)build bibliotheque-composants
"""
import copy
import sys
import uuid

from sb import api, all_pages

SOURCES = ["home", "credit-immobilier", "assurance-de-pret", "rachat-de-credit", "simulation-credit-immobilier",
           "site-config", "parametres/bareme-des-taux", "actualites/rachat-de-credits-banques-plus-strictes"]
PRESET_NAME = "Modèle Meilleurtaux"

# Blocks never used on a page yet: hand-written presets.
# Page types that also get a selectable template (never the default).
ROOT_PRESETS = {"mt-offer-page": "Modèle offre"}

EXTRA = {
    "mt-offer-page": {
        "component": "mt-offer-page", "product": "credit-consommation", "offer_label": "Offre de bienvenue",
        "amount": "Frais de dossier offerts", "promo_code": "BIENVENUE2026",
        "starts_on": "2026-10-01 00:00", "ends_on": "2026-12-31 23:59",
        "summary": {"type": "doc", "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "Pour toute demande de crédit à la consommation déposée avant le 31/12/2026 avec le code ci-dessous."}]}]},
        "cta_label": "J'en profite",
        "cta_link": {"linktype": "url", "url": "#simulateur", "fieldtype": "multilink"},
        "conditions": {"type": "doc", "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "Offre réservée aux nouveaux clients, sous réserve d'acceptation du dossier par l'organisme prêteur. Une seule utilisation par foyer."}]}]},
        "legal_mentions": {"type": "doc", "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "Un crédit vous engage et doit être remboursé. Vérifiez vos capacités de remboursement avant de vous engager."}]}]},
    },
    "mt-text": {"component": "mt-text", "eyebrow": "Le guide de l'emprunteur", "title": "Bien préparer son projet immobilier",
                "body": {"type": "doc", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "Avant de rencontrer une banque, faites le point sur votre apport, vos revenus et vos charges. Un courtier vous aide à présenter un dossier solide et à négocier les meilleures conditions."}]}]},
                "background": "white", "width": "narrow", "space_top": "m", "space_bottom": "m", "align": "left", "title_size": "m"},
}

LABELS = {
    "mt-hero": "Bandeau d'ouverture (Hero)", "mt-simulator": "Simulateur", "mt-rates": "Tableau des taux",
    "mt-market-rate": "Taux du marché (données BCE)", "mt-trust": "Bandeau de confiance", "mt-feature-card": "Carte mise en avant", "mt-logos": "Logos partenaires",
    "mt-carousel": "Carrousel de cartes", "mt-card-grid": "Grille de cartes", "mt-steps": "Étapes + vidéo",
    "mt-accordion": "Questions / accordéon", "mt-news": "Actualités", "mt-guides": "Guides", "mt-reviews": "Avis clients",
    "mt-app-promo": "Applications mobiles", "mt-alert": "Bandeau d'information", "mt-toc": "Sommaire",
    "mt-text": "Texte", "mt-cta": "Appel à l'action",
}

# Library: which option to vary per section (all its values are shown).
VARY = {"mt-hero": "layout", "mt-simulator": "type", "mt-rates": "layout", "mt-market-rate": "indicator", "mt-feature-card": "layout",
        "mt-logos": "layout", "mt-carousel": "layout", "mt-card-grid": None, "mt-accordion": "layout",
        "mt-cta": "layout", "mt-alert": "tone"}


def strip(b):
    """Deep copy without _uid / _editable, so the preset gets fresh ids."""
    if isinstance(b, dict):
        return {k: strip(v) for k, v in b.items() if k not in ("_uid", "_editable")}
    if isinstance(b, list):
        return [strip(x) for x in b]
    return b


def walk(b, found):
    if isinstance(b, dict):
        c = b.get("component")
        if c and c.startswith("mt-") and c not in found:
            found[c] = strip(b)
        for v in b.values():
            walk(v, found)
    elif isinstance(b, list):
        for x in b:
            walk(x, found)


def collect():
    found = {}
    for slug in SOURCES:
        s = api("GET", f"/stories/?with_slug={slug}")["stories"]
        if not s:
            print("missing source", slug, file=sys.stderr)
            continue
        content = api("GET", f"/stories/{s[0]['id']}")["story"]["content"]
        for v in content.values():  # skip the page root itself
            walk(v, found)
    found.update(EXTRA)  # hand-written presets win over page instances
    # The grid preset should be the simulator cards (icon layout), not whichever grid came first.
    return found


def push_presets(found):
    comps = {c["name"]: c for c in all_pages("/components/", "components")}
    existing = {(p["component_id"], p["name"]): p for p in api("GET", "/presets/").get("presets", [])}
    for name, comp in comps.items():
        if not name.startswith("mt-") or (comp.get("is_root") and name not in ROOT_PRESETS) or name not in found:
            continue
        body = {"preset": {"name": ROOT_PRESETS.get(name, PRESET_NAME), "component_id": comp["id"], "preset": found[name]}}
        if comp.get("image"):
            # The block picker hover shows the PRESET image, so it must live on the preset too.
            body["preset"]["image"] = comp["image"]
        cur = existing.get((comp["id"], ROOT_PRESETS.get(name, PRESET_NAME)))
        if cur:
            api("PUT", f"/presets/{cur['id']}", body)
            pid = cur["id"]
        else:
            pid = api("POST", "/presets/", body)["preset"]["id"]
        # Presets stay selectable in the picker, but none is the default: adding a block
        # gives a blank one, so editors choose a preset OR start from scratch (operator rule, 2026-10-29).
        if comp.get("preset_id"):
            keep = {k: comp[k] for k in ("name", "schema", "display_name", "is_root", "is_nestable", "component_group_uuid",
                                         "icon", "color", "preview_field", "description", "image") if k in comp}
            api("PUT", f"/components/{comp['id']}", {"component": {**keep, "preset_id": None}})
        print("preset", name, pid)
    missing = [n for n, c in comps.items() if n.startswith("mt-") and not c.get("is_root") and n not in found]
    if missing:
        print("no preset for", missing)


def with_uids(b):
    if isinstance(b, dict):
        out = {k: with_uids(v) for k, v in b.items()}
        if "component" in out:
            out["_uid"] = str(uuid.uuid4())
        return out
    if isinstance(b, list):
        return [with_uids(x) for x in b]
    return b


def divider(i, name, values):
    return {"component": "mt-text", "eyebrow": f"{i:02d}", "title": LABELS[name], "background": "cream", "width": "standard",
            "space_top": "m", "space_bottom": "s", "align": "left", "title_size": "m",
            "body": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": values}]}]}}


def library_body(found):
    comps = {c["name"]: c for c in all_pages("/components/", "components")}
    body = []
    for i, name in enumerate(LABELS, 1):
        if name not in found:
            continue
        field = VARY.get(name)
        opts = comps[name]["schema"].get(field, {}).get("options", []) if field else []
        body.append(divider(i, name, " · ".join(o["name"] for o in opts) or comps[name].get("description", "")))
        variants = [(o["value"], o["name"]) for o in opts] or [(None, None)]
        for n, (value, _label) in enumerate(variants):
            b = copy.deepcopy(found[name])
            if field and value:
                b[field] = value
            if name == "mt-hero" and value == "products" and not b.get("tiles"):
                b.update({k: copy.deepcopy(found["mt-hero-products"][k]) for k in ("tiles", "promo", "headline")})
            if n == 0:
                b["anchor"] = f"lib-{name}"  # used by the picker screenshots
            body.append(b)
    return [with_uids(b) for b in body]


def push_library(found):
    content = {"component": "mt-page", "meta_title": "Bibliothèque de composants | Meilleurtaux", "noindex": True,
               "body": library_body(found)}
    hit = api("GET", "/stories/?with_slug=bibliotheque-composants").get("stories", [])
    if hit:
        api("PUT", f"/stories/{hit[0]['id']}", {"story": {"content": content}, "publish": 1, "force_update": "1"})
        print("library updated", hit[0]["id"])
    else:
        s = api("POST", "/stories/", {"story": {"name": "Bibliothèque de composants", "slug": "bibliotheque-composants",
                                                "content": content}, "publish": 1})
        print("library created", s["story"]["id"])


if __name__ == "__main__":
    found = collect()
    # Default Hero preset = the product-page hero (photo, choices); the home hero feeds the tile variant.
    found["mt-hero-products"] = found["mt-hero"]
    ci = api("GET", "/stories/?with_slug=credit-immobilier")["stories"][0]
    found["mt-hero"] = strip(api("GET", f"/stories/{ci['id']}")["story"]["content"]["hero"][0])
    push_presets({k: v for k, v in found.items() if k != "mt-hero-products"})
    if "--library" in sys.argv:
        push_library(found)
