"""Meilleurtaux block library: component schemas and groups.

Single source of truth. Re-run after any change; it updates in place.
Design rule: every block = a few named Layouts + one short Style tab + Visibility.
Text colour follows the background automatically, so editors never pick text colours.
Editor labels are in French (the prospect's marketing team works in French).
"""
import sys

from sb import api, all_pages

# ---------------------------------------------------------------- field kit


def opts(*pairs):
    return [{"value": v, "name": n} for v, n in pairs]


def hide_when(*conds):
    """Hide the field when ANY (field, 'equals'|'not_equals', value) condition holds."""
    return [{"modifications": [{"display": "hide"}], "rule_match": "any",
             "rule_conditions": [{"validated_object": {"type": "field", "field_key": f, "field_attr": "value"},
                                  "validation": v, "value": val} for f, v, val in conds]}]


def hide_unless(field, *values):
    """Show the field only when `field` has one of `values`."""
    return [{"modifications": [{"display": "hide"}], "rule_match": "all",
             "rule_conditions": [{"validated_object": {"type": "field", "field_key": field, "field_attr": "value"},
                                  "validation": "not_equals", "value": v} for v in values]}]


def text(name, desc="", **kw):
    return {"type": "text", "display_name": name, "description": desc, "translatable": True, **kw}


def area(name, desc="", **kw):
    return {"type": "textarea", "display_name": name, "description": desc, "translatable": True, **kw}


SHORT_TOOLBAR = ["bold", "italic", "link", "list", "olist"]
LONG_TOOLBAR = ["paragraph", "h2", "h3", "bold", "italic", "link", "list", "olist", "quote", "hrule", "image"]


def rich(name, desc="", long=False, **kw):
    return {"type": "richtext", "display_name": name, "description": desc, "translatable": True,
            "customize_toolbar": True, "toolbar": LONG_TOOLBAR if long else SHORT_TOOLBAR, **kw}


def media(name, desc="", videos=True, **kw):
    return {"type": "asset", "display_name": name, "description": desc,
            "filetypes": ["images", "videos"] if videos else ["images"], **kw}


def option(name, choices, default, desc="", **kw):
    return {"type": "option", "display_name": name, "description": desc, "options": opts(*choices),
            "default_value": default, "exclude_empty_option": True, **kw}


def number(name, desc="", default=None, **kw):
    f = {"type": "number", "display_name": name, "description": desc, **kw}
    if default is not None:
        f["default_value"] = str(default)
    return f


def boolean(name, desc="", default=False):
    return {"type": "boolean", "display_name": name, "description": desc, "default_value": default}


def link(name, desc="", **kw):
    return {"type": "multilink", "display_name": name, "description": desc, "show_anchor": True,
            "email_link_type": True, "asset_link_type": True, "allow_target_blank": False, **kw}


def bloks(name, allowed, desc="", maximum=None, minimum=None, **kw):
    f = {"type": "bloks", "display_name": name, "description": desc, "restrict_components": True,
         "component_whitelist": allowed, **kw}
    if maximum:
        f["maximum"] = maximum
    if minimum:
        f["minimum"] = minimum
    return f


EYEBROW = lambda: text("Petit titre au-dessus", "Court. Affiché en terracotta au-dessus du titre. Laissez vide pour le masquer.")  # noqa: E731
HEADLINE = lambda d="": area("Titre", d or "Appuyez sur Entrée pour passer à la ligne.")  # noqa: E731
HIGHLIGHT = lambda: text(  # noqa: E731
    "Mots mis en valeur",
    "Affichés en terracotta. Tapez les mots exactement comme dans le titre. Séparez-en plusieurs avec |  (ex. crédit immobilier).")
BUTTONS = lambda m=2: bloks("Boutons", ["mt-button"], f"Jusqu'à {m} boutons. Le premier est l'action principale.", maximum=m)  # noqa: E731

BACKGROUNDS = [("white", "Blanc"), ("cream", "Crème (fond Meilleurtaux)"), ("peach", "Pêche"),
               ("terracotta", "Terracotta"), ("brown", "Brun profond"), ("image", "Image ou vidéo")]


def style_tab(background="white", space_top="m", space_bottom="m", width="standard", align="left",
              title_size="m", with_title=True, with_align=True):
    f = {
        "background": option("Fond", BACKGROUNDS, background,
                             "La couleur du texte s'adapte toute seule : chaque choix reste lisible."),
        "background_image": media("Image ou vidéo de fond", "Affichée derrière le contenu. Choisissez une image large et calme.",
                                  conditional_settings=hide_unless("background", "image")),
        "overlay": option("Assombrir l'image", [("dark", "Fort (idéal pour beaucoup de texte)"), ("light", "Léger")], "dark",
                          conditional_settings=hide_unless("background", "image")),
        "space_top": option("Espace au-dessus", [("none", "Aucun"), ("s", "Petit"), ("m", "Moyen"), ("l", "Grand")], space_top),
        "space_bottom": option("Espace en dessous", [("none", "Aucun"), ("s", "Petit"), ("m", "Moyen"), ("l", "Grand")], space_bottom),
        "width": option("Largeur du contenu", [("narrow", "Étroite (lecture)"), ("standard", "Standard"),
                                               ("wide", "Large"), ("full", "Toute la largeur de l'écran")], width),
    }
    if with_align:
        f["align"] = option("Alignement", [("left", "À gauche"), ("center", "Centré")], align)
    if with_title:
        f["title_size"] = option("Taille du titre", [("s", "Petit"), ("m", "Moyen"), ("l", "Grand"), ("xl", "Très grand")], title_size)
    return f


def visibility_tab():
    return {
        "hide_mobile": boolean("Masquer sur mobile"),
        "hide_desktop": boolean("Masquer sur ordinateur"),
        "show_from": {"type": "datetime", "display_name": "Afficher à partir du",
                      "description": "Laissez vide pour afficher tout de suite. L'éditeur affiche toujours la section, avec un badge."},
        "show_until": {"type": "datetime", "display_name": "Afficher jusqu'au", "description": "Laissez vide pour la garder en ligne."},
        "anchor": text("Nom d'ancre", "Permet aux boutons et au Sommaire de pointer ici avec #nom. Minuscules, sans espaces.",
                       translatable=False),
        "toc_label": text("Libellé dans le Sommaire", "Laissez vide pour reprendre le titre de la section."),
    }


def section(general, style=None, extra_tabs=None):
    """General fields + Style tab + Visibility tab, in that order."""
    schema, pos = {}, 0
    for k, v in general.items():
        schema[k] = {**v, "pos": pos}
        pos += 1
    tabs = [("Style", style or style_tab())] + (extra_tabs or []) + [("Visibilité", visibility_tab())]
    for title, fields in tabs:
        keys = []
        for k, v in fields.items():
            schema[k] = {**v, "pos": pos}
            keys.append(k)
            pos += 1
        slug = title.lower().replace(" ", "-").replace("é", "e").replace("è", "e")
        schema[f"tab-{slug}"] = {"type": "tab", "display_name": title, "keys": keys, "pos": pos}
        pos += 1
    return schema


def plain(fields, tabs=None):
    schema, pos = {}, 0
    for k, v in fields.items():
        schema[k] = {**(v or {}), "pos": pos}
        pos += 1
    for title, tf in (tabs or []):
        keys = []
        for k, v in tf.items():
            schema[k] = {**v, "pos": pos}
            keys.append(k)
            pos += 1
        slug = title.lower().replace(" ", "-").replace("é", "e").replace("è", "e").replace("'", "")
        schema[f"tab-{slug}"] = {"type": "tab", "display_name": title, "keys": keys, "pos": pos}
        pos += 1
    return schema


def layout(choices, default, desc="Choisissez la disposition. Le contenu reste le même quand vous changez."):
    return option("Disposition", choices, default, desc)


DURATIONS = [("15", "15 ans"), ("20", "20 ans"), ("25", "25 ans")]
CATEGORIES = [("credit-immobilier", "Crédit immobilier"), ("assurance-de-pret", "Assurance de prêt"),
              ("rachat-de-credit", "Rachat de crédit"), ("assurances", "Assurances"),
              ("placement", "Placement et épargne"), ("credit-consommation", "Crédit consommation")]

SEO_TAB = ("SEO", {
    "meta_title": text("Titre dans Google", "Environ 55 caractères. Vide = nom de la page.", max_length=70),
    "meta_description": area("Description dans Google", "Environ 150 caractères.", max_length=170),
    "og_image": media("Image de partage", "Affichée sur LinkedIn, Facebook, WhatsApp...", videos=False),
    "noindex": boolean("Ne pas référencer cette page"),
})

# ---------------------------------------------------------------- sections
SECTIONS = {
    "mt-hero": dict(
        display_name="Bandeau d'ouverture (Hero)", icon="block-text-img-r", color="#c0543a", preview_field="headline",
        description="La grande section d'ouverture d'une page : tuiles produits, photo, ou choix rapide.",
        schema=section({
            "layout": layout([("products", "Titre + tuiles produits + offre (accueil)"),
                              ("split", "Texte avec photo à côté (page produit)"),
                              ("background", "Photo en fond, texte par-dessus"),
                              ("centered", "Texte centré, sans photo")], "split"),
            "label": text("Étiquette", "Petite étiquette encadrée au-dessus du titre, ex. Prêt immobilier.",
                          conditional_settings=hide_when(("layout", "equals", "products"))),
            "headline": HEADLINE(), "highlight": HIGHLIGHT(),
            "intro": rich("Texte d'introduction", "Mettez en gras les mots à faire ressortir : ils s'affichent en terracotta.",
                          conditional_settings=hide_when(("layout", "equals", "products"))),
            "tiles": bloks("Tuiles produits", ["mt-product-tile"],
                           "Une tuile par produit. Cochez « Grande tuile » pour le produit phare (il peut afficher le taux du jour).",
                           conditional_settings=hide_unless("layout", "products")),
            "promo": bloks("Offre mise en avant", ["mt-promo-card"], "Une offre à droite des tuiles. Laissez vide pour la masquer.",
                           maximum=1, conditional_settings=hide_unless("layout", "products")),
            "choices_label": text("Question avant les choix", "Ex. Vous empruntez…",
                                  conditional_settings=hide_when(("layout", "equals", "products"))),
            "choices": bloks("Choix rapides", ["mt-choice"], "Grands boutons avec icône, ex. Seul(e) / Avec un co-emprunteur.",
                             maximum=3, conditional_settings=hide_when(("layout", "equals", "products"))),
            "buttons": BUTTONS(),
            "trust": boolean("Afficher la note Trustpilot", "La note vient des Paramètres du site.", default=False),
            "media": media("Photo ou vidéo", "Photo à droite (Texte avec photo) ou en fond (Photo en fond). Une vidéo MP4 joue en boucle, sans le son.",
                           conditional_settings=hide_unless("layout", "split", "background")),
        }, style_tab(background="cream", space_top="m", space_bottom="m", width="standard", title_size="l", with_align=False))),

    "mt-simulator": dict(
        display_name="Simulateur", icon="block-dollar-sign", color="#c0543a", preview_field="title",
        description="Un vrai calculateur : le visiteur déplace les curseurs, le résultat se met à jour. Les taux viennent du Barème des taux.",
        schema=section({
            "type": option("Type de simulation", [("project", "Définir son projet (mensualité ou montant)"),
                                                  ("monthly", "Calcul des mensualités"),
                                                  ("capacity", "Capacité d'emprunt"),
                                                  ("insurance", "Économies sur l'assurance de prêt"),
                                                  ("consolidation", "Rachat de crédits (nouvelle mensualité)")], "project",
                           "Chaque type affiche ses propres curseurs. Le calcul est indicatif (aucune donnée n'est envoyée)."),
            "layout": layout([("with_rates", "Simulateur + tableau des taux à côté"), ("alone", "Simulateur seul, centré"),
                              ("result", "Simulateur + grand résultat détaillé")], "with_rates"),
            "title": text("Titre du simulateur", "Ex. Définir votre projet de crédit immo"),
            "rates_title": text("Titre du tableau des taux", "Ex. Les taux nationaux pour un prêt immo",
                                conditional_settings=hide_unless("layout", "with_rates")),
            "default_amount": number("Montant par défaut (€)", "Valeur de départ du curseur.", 200000),
            "default_monthly": number("Mensualité par défaut (€)", "", 1000,
                                      conditional_settings=hide_unless("type", "project", "capacity")),
            "default_income": number("Revenus mensuels par défaut (€)", "", 4000, conditional_settings=hide_unless("type", "capacity")),
            "default_duration": option("Durée par défaut", DURATIONS, "20"),
            "rate_profile": option("Profil de taux utilisé", [("excellent", "Excellent"), ("tres-bon", "Très bon"), ("bon", "Bon")],
                                   "tres-bon", "Le taux est lu dans le Barème des taux (Paramètres > Barème des taux)."),
            "button_label": text("Texte du bouton", "Ex. Faire une simulation"),
            "button_link": link("Lien du bouton", "Page du parcours complet."),
            "rates_button_label": text("Texte du bouton des taux", "Ex. Estimer son taux",
                                       conditional_settings=hide_unless("layout", "with_rates")),
            "rates_button_link": link("Lien du bouton des taux", conditional_settings=hide_unless("layout", "with_rates")),
            "disclaimer": rich("Mention sous le résultat", "Ex. Simulation indicative, hors assurance. Un crédit vous engage…"),
        }, style_tab(background="white", width="standard", with_title=False, with_align=False))),

    "mt-rates": dict(
        display_name="Tableau des taux", icon="block-table", color="#c0543a", preview_field="title",
        description="Taux du moment par durée, lus dans le Barème des taux : modifiés une fois, mis à jour partout.",
        schema=section({
            "layout": layout([("tabs", "Onglets par durée (15 / 20 / 25 ans)"), ("table", "Tableau complet (durées × profils)"),
                              ("cost", "Coût total d'un prêt selon la durée")], "table"),
            "eyebrow": EYEBROW(), "title": text("Titre"), "intro": rich("Texte d'introduction"),
            "cost_amount": number("Montant du prêt pour le calcul (€)", "Ex. 200000", 200000, conditional_settings=hide_unless("layout", "cost")),
            "show_trend": boolean("Afficher la tendance (en hausse / stable / en baisse)", default=True),
            "show_date": boolean("Afficher la date de mise à jour des taux", default=True),
            "note": rich("Mention sous le tableau"),
            "buttons": BUTTONS(1),
        }, style_tab(background="white", width="standard", align="left"))),

    "mt-trust": dict(
        display_name="Bandeau de confiance", icon="block-check", color="#c0543a", preview_field="headline",
        description="Grand message de confiance, 3 arguments avec icône et la note Trustpilot.",
        schema=section({
            "headline": HEADLINE("Ex. Plus de 3 millions de Français nous font confiance chaque année depuis plus de 20 ans."),
            "highlight": HIGHLIGHT(),
            "features": bloks("Arguments", ["mt-feature"], "3 arguments conseillés.", maximum=4),
            "trust": boolean("Afficher la note Trustpilot", default=True),
        }, style_tab(background="white", align="center", title_size="m"))),

    "mt-feature-card": dict(
        display_name="Carte mise en avant", icon="block-image", color="#c0543a", preview_field="title",
        description="Un message fort dans une carte : étude, agences, recrutement, définition produit…",
        schema=section({
            "layout": layout([("image_left", "Image à gauche"), ("image_right", "Image à droite"),
                              ("image_edge", "Grande image collée à droite (recrutement)"),
                              ("text", "Texte seul, centré"), ("rating", "Texte + note clients à côté"),
                              ("quote", "Citation d'expert (photo ronde, guillemets)")], "image_left"),
            "icon": media("Icône", "Petite icône à côté du titre (optionnelle).", videos=False),
            "eyebrow": EYEBROW(), "title": text("Titre"), "highlight": HIGHLIGHT(),
            "text": rich("Texte", "Les listes à puces sont bien mises en forme."),
            "buttons": BUTTONS(),
            "media": media("Image ou vidéo", "Pour la Citation d'expert : la photo de l'expert (carrée).",
                           conditional_settings=hide_when(("layout", "equals", "text"), ("layout", "equals", "rating"))),
            "quote_name": text("Nom de l'expert", "Ex. Guillaume Fourt", translatable=False, conditional_settings=hide_unless("layout", "quote")),
            "quote_role": text("Fonction de l'expert", "Ex. Directeur des Partenariats Bancaires", conditional_settings=hide_unless("layout", "quote")),
            "card_color": option("Couleur de la carte", [("cream", "Crème"), ("white", "Blanc avec ombre"), ("peach", "Pêche")], "cream"),
        }, style_tab(background="white", with_align=False, title_size="m"))),

    "mt-logos": dict(
        display_name="Logos partenaires", icon="block-image", color="#c0543a", preview_field="title",
        description="Banques et assureurs partenaires, en défilement ou en grille.",
        schema=section({
            "layout": layout([("marquee", "Défilement continu"), ("grid", "Grille fixe")], "marquee"),
            "title": text("Titre", "Ex. Nos partenaires bancaires. Laissez vide pour masquer."),
            "intro": rich("Texte d'introduction"),
            "logos": {"type": "multiasset", "display_name": "Logos", "description": "Des logos SVG ou PNG transparents s'affichent le mieux.",
                      "filetypes": ["images"]},
            "grayscale": boolean("Logos en gris (couleur au survol)", default=False),
            "buttons": BUTTONS(1),
        }, style_tab(background="white", align="center", title_size="s"))),

    "mt-carousel": dict(
        display_name="Carrousel de cartes", icon="block-carousel", color="#c0543a", preview_field="title",
        description="Cartes qui défilent : projets de vie, profils d'emprunteurs, contenus à découvrir.",
        schema=section({
            "layout": layout([("stories", "Projets de vie (photo + citation)"), ("profiles", "Profils (photo en haut + texte)"),
                              ("links", "Cartes liens (photo + titre)")], "stories"),
            "title": text("Titre"), "intro": rich("Texte d'introduction"),
            "cards": bloks("Cartes", ["mt-card"], "Glissez pour réordonner."),
            "buttons": BUTTONS(1),
        }, style_tab(background="white", title_size="m"))),

    "mt-card-grid": dict(
        display_name="Grille de cartes", icon="block-table-2", color="#c0543a", preview_field="title",
        description="Cartes alignées : simulateurs, types de prêt, exemples clients, étapes.",
        schema=section({
            "layout": layout([("icon", "Icône centrée + bouton (simulateurs)"), ("list", "Titre en couleur + liste (types de prêt)"),
                              ("case", "Exemple client avec photo ronde"), ("steps", "Étapes numérotées avec icône"),
                              ("photo", "Photo en haut + texte"), ("tiles", "Tuiles liens compactes (guide)")], "icon"),
            "eyebrow": EYEBROW(), "title": text("Titre"), "highlight": HIGHLIGHT(), "intro": rich("Texte d'introduction"),
            "columns": option("Cartes par ligne (ordinateur)", [("2", "2"), ("3", "3"), ("4", "4")], "3"),
            "cards": bloks("Cartes", ["mt-card"]),
            "buttons": BUTTONS(1),
        }, style_tab(background="white", title_size="m"))),

    "mt-steps": dict(
        display_name="Étapes + vidéo", icon="block-flow", color="#c0543a", preview_field="title",
        description="Étapes numérotées dépliables, avec une vidéo ou une image à côté.",
        schema=section({
            "title": text("Titre", "Ex. Comment réaliser une simulation de crédit immobilier ?"),
            "steps": bloks("Étapes", ["mt-step"], "Chaque étape se déplie au clic."),
            "buttons": BUTTONS(1),
            "media_source": option("Média", [("youtube", "Vidéo YouTube"), ("asset", "Image ou vidéo de la médiathèque")], "youtube"),
            "youtube": text("Lien ou identifiant YouTube", "Collez le lien (youtube.com/watch?v=… ou youtu.be/…).", translatable=False,
                            conditional_settings=hide_unless("media_source", "youtube")),
            "poster": media("Image d'aperçu de la vidéo", "Affichée avant la lecture. Vide = image YouTube.", videos=False,
                            conditional_settings=hide_unless("media_source", "youtube")),
            "media": media("Image ou vidéo", conditional_settings=hide_unless("media_source", "asset")),
            "media_side": option("Côté du média", [("right", "À droite"), ("left", "À gauche")], "right"),
            "media_color": option("Couleur derrière le média", [("peach", "Pêche"), ("cream", "Crème"), ("terracotta", "Terracotta")], "peach"),
        }, style_tab(background="cream", space_top="none", space_bottom="none", width="full", title_size="m", with_align=False))),

    "mt-accordion": dict(
        display_name="Questions / accordéon", icon="block-keyboard", color="#c0543a", preview_field="title",
        description="Questions fréquentes ou points détaillés qui se déplient.",
        schema=section({
            "layout": layout([("faq", "Titre à gauche, questions à droite"), ("simple", "Liste simple"),
                              ("images", "Questions + deux images en quinconce")], "faq"),
            "eyebrow": EYEBROW(), "title": text("Titre"), "intro": rich("Texte d'introduction"),
            "items": bloks("Questions", ["mt-faq-item"]),
            "image_1": media("Image 1", videos=False, conditional_settings=hide_unless("layout", "images")),
            "image_2": media("Image 2", videos=False, conditional_settings=hide_unless("layout", "images")),
            "buttons": BUTTONS(2),
            "schema_faq": boolean("Ajouter les données FAQ pour Google", "Aide à apparaître dans les résultats enrichis.", default=True),
        }, style_tab(background="white", title_size="m", with_align=False))),

    "mt-news": dict(
        display_name="Actualités", icon="block-doc", color="#c0543a", preview_field="title",
        description="Les derniers articles, automatiquement ou choisis à la main.",
        schema=section({
            "title": text("Titre", "Ex. Actualités"),
            "source": option("Articles affichés", [("latest", "Les plus récents (automatique)"), ("picked", "Choisis à la main")], "latest"),
            "category": option("Thème", [("all", "Tous les thèmes")] + CATEGORIES, "all",
                               "Ne garder que les articles de ce thème.", conditional_settings=hide_unless("source", "latest")),
            "articles": {"type": "options", "display_name": "Articles", "source": "internal_stories", "filter_content_type": ["mt-article"],
                         "description": "Dans l'ordre choisi.", "conditional_settings": hide_unless("source", "picked")},
            "count": option("Nombre d'articles", [("3", "3"), ("6", "6"), ("9", "9"), ("12", "12")], "3",
                            conditional_settings=hide_unless("source", "latest")),
            "filters": boolean("Afficher les filtres par thème", "Pour la page Actualités.", default=False),
            "buttons": BUTTONS(1),
        }, style_tab(background="white", title_size="m"))),

    "mt-guides": dict(
        display_name="Guides (colonnes de liens)", icon="block-list", color="#c0543a", preview_field="title",
        description="Colonnes de liens avec icône, comme « Nos guides ».",
        schema=section({
            "title": text("Titre"),
            "columns": bloks("Colonnes", ["mt-link-column"], "3 par ligne sur ordinateur."),
            "card": boolean("Dans une carte blanche avec ombre", default=True),
        }, style_tab(background="cream", title_size="m"))),

    "mt-reviews": dict(
        display_name="Avis clients", icon="block-quote", color="#c0543a", preview_field="title",
        description="Panneau d'introduction + avis clients qui défilent, avec la note Trustpilot.",
        schema=section({
            "title": text("Titre", "Ex. Nos clients en parlent"),
            "text": rich("Texte"),
            "reviews": bloks("Avis", ["mt-review"]),
            "link_label": text("Texte du lien", "Ex. Méthodologie"),
            "link": link("Lien"),
        }, style_tab(background="white", width="full", title_size="m", with_align=False))),

    "mt-app-promo": dict(
        display_name="Applications mobiles", icon="block-mobile", color="#c0543a", preview_field="title",
        description="Présentation des applications avec boutons App Store / Google Play et visuel téléphone.",
        schema=section({
            "title": text("Titre", "Ex. Tout Meilleurtaux dans votre poche"),
            "apps": bloks("Applications", ["mt-app"], maximum=4),
            "media": media("Visuel téléphones", videos=True),
        }, style_tab(background="white", title_size="m", with_align=False))),

    "mt-alert": dict(
        display_name="Bandeau d'information", icon="block-warning", color="#c0543a", preview_field="title",
        description="Message important : vigilance fraude, mention légale, information réglementaire.",
        schema=section({
            "tone": option("Type de message", [("warning", "Vigilance (triangle)"), ("info", "Information (i)"),
                                               ("legal", "Mention légale (sans icône)")], "warning"),
            "title": text("Titre"),
            "text": rich("Texte"),
        }, style_tab(background="cream", space_top="s", space_bottom="s", width="standard", with_title=False, with_align=False))),

    "mt-toc": dict(
        display_name="Sommaire", icon="block-list", color="#c0543a", preview_field="title",
        description="Se remplit tout seul avec les sections de la page qui ont un nom d'ancre (onglet Visibilité).",
        schema=section({
            "title": text("Titre", "Ex. Sommaire"),
            "collapsed": boolean("Replié au départ sur mobile", default=True),
        }, style_tab(background="cream", space_top="s", space_bottom="s", width="wide", with_title=False, with_align=False))),

    "mt-text": dict(
        display_name="Texte", icon="block-text-c", color="#c0543a", preview_field="title",
        description="Titre et texte riche, pour les contenus éditoriaux.",
        schema=section({
            "eyebrow": EYEBROW(), "title": text("Titre"), "highlight": HIGHLIGHT(),
            "body": rich("Texte", long=True),
            "buttons": BUTTONS(),
        }, style_tab(background="white", width="narrow", title_size="m"))),

    "mt-cta": dict(
        display_name="Appel à l'action", icon="block-flag", color="#c0543a", preview_field="title",
        description="Bandeau de fin de page avec un titre et un ou deux boutons.",
        schema=section({
            "layout": layout([("band", "Bandeau centré"), ("split", "Texte + image"), ("pill", "Bandeau compact sur une ligne")], "band"),
            "eyebrow": EYEBROW(), "title": text("Titre"), "highlight": HIGHLIGHT(), "text": rich("Texte"),
            "buttons": BUTTONS(),
            "media": media("Image", videos=True, conditional_settings=hide_unless("layout", "split")),
        }, style_tab(background="terracotta", align="center", title_size="m"))),
}

# ---------------------------------------------------------------- items
ITEMS = {
    "mt-button": dict(display_name="Bouton", icon="block-arrow-pointer", color="#5a2a17", preview_field="label",
                      schema=plain({
                          "label": text("Texte du bouton", required=True, max_length=48),
                          "link": link("Lien", "Choisissez une page, collez une URL, ou ajoutez #nom pour aller à une section."),
                          "style": option("Apparence", [("primary", "Bouton terracotta"), ("dark", "Bouton brun (simulation)"),
                                                        ("outline", "Bouton contour"), ("link", "Lien avec flèche")], "primary"),
                          "arrow": boolean("Ajouter une flèche →"),
                          "new_tab": boolean("Ouvrir dans un nouvel onglet"),
                      })),
    "mt-product-tile": dict(display_name="Tuile produit", icon="block-sticker", color="#5a2a17", preview_field="label",
                            schema=plain({
                                "label": area("Nom du produit", "Entrée pour passer à la ligne, ex. Crédit⏎immobilier.", required=True),
                                "icon": media("Icône", "Icône Meilleurtaux (SVG).", videos=False),
                                "link": link("Lien"),
                                "size": option("Taille", [("normal", "Normale"), ("large", "Grande tuile (2 colonnes)"),
                                                          ("row", "Ligne (icône à gauche)")], "normal"),
                                "show_rate": boolean("Afficher le taux du jour", "Lu dans le Barème des taux (profil Excellent)."),
                                "rate_duration": option("Durée du taux affiché", DURATIONS, "15",
                                                        "Utilisée seulement si « Afficher le taux du jour » est coché."),
                                "badge": text("Badge", "Ex. Nouveau. Laissez vide pour masquer."),
                            })),
    "mt-promo-card": dict(display_name="Carte offre", icon="block-sticker", color="#5a2a17", preview_field="title",
                          schema=plain({
                              "tag": text("Étiquette", "Ex. Assurance Vie"),
                              "eyebrow": text("Petit titre", "Ex. Offre de bienvenue"),
                              "title": text("Titre de l'offre", "Ex. 200 € offerts"),
                              "text": rich("Conditions", "Ex. du 21/09 au 15/12/2026 avec le code **SPIRICA2026**"),
                              "button": bloks("Bouton", ["mt-button"], maximum=1),
                              "small_print": rich("Mention en bas"),
                              "image": media("Image de fond", videos=True),
                          })),
    "mt-choice": dict(display_name="Choix rapide", icon="block-arrow-pointer", color="#5a2a17", preview_field="label",
                      schema=plain({
                          "label": text("Texte", required=True),
                          "icon": option("Icône", [("person", "Une personne"), ("people", "Deux personnes"), ("home", "Maison"),
                                                   ("key", "Clé"), ("euro", "Euro"), ("shield", "Bouclier")], "person"),
                          "link": link("Lien"),
                      })),
    "mt-feature": dict(display_name="Argument", icon="block-check", color="#5a2a17", preview_field="title",
                       schema=plain({
                           "icon": option("Icône", [("screen", "Écran"), ("trophy", "Trophée"), ("chat", "Bulles"), ("shield", "Bouclier"),
                                                    ("euro", "Euro"), ("clock", "Horloge"), ("agency", "Agence"), ("star", "Étoile")], "screen"),
                           "title": text("Titre", required=True),
                           "text": area("Texte"),
                       })),
    "mt-card": dict(display_name="Carte", icon="block-sticker", color="#5a2a17", preview_field="title",
                    schema=plain({
                        "image": media("Photo ou icône", "Photo (carrousel, exemples) ou icône (simulateurs, étapes).", videos=False),
                        "tag": text("Étiquette", "Ex. Mutuelle santé (sur la photo)."),
                        "title": text("Titre"),
                        "quote": area("Citation", "Affichée en italique, ex. « Ma nouvelle mutuelle… »."),
                        "text": rich("Texte", "Les listes à puces sont bien mises en forme."),
                        "link_label": text("Texte du lien", "Vide = pas de lien."),
                        "link": link("Lien"),
                    })),
    "mt-step": dict(display_name="Étape", icon="block-flow", color="#5a2a17", preview_field="title",
                    schema=plain({"title": text("Titre de l'étape", required=True), "text": rich("Détail (visible une fois déplié)")})),
    "mt-faq-item": dict(display_name="Question", icon="block-keyboard", color="#5a2a17", preview_field="question",
                        schema=plain({"question": text("Question", required=True), "answer": rich("Réponse")})),
    "mt-link-column": dict(display_name="Colonne de liens", icon="block-list", color="#5a2a17", preview_field="title",
                           schema=plain({
                               "icon": media("Icône", videos=False),
                               "title": text("Titre"),
                               "link": link("Lien du titre", "Optionnel."),
                               "links": bloks("Liens", ["mt-nav-link"]),
                           })),
    "mt-review": dict(display_name="Avis", icon="block-quote", color="#5a2a17", preview_field="name",
                      schema=plain({
                          "text": area("Avis", required=True),
                          "name": text("Prénom ou pseudo", translatable=False),
                          "rating": option("Note", [("5", "5 étoiles"), ("4", "4 étoiles"), ("3", "3 étoiles")], "5"),
                          "date": text("Date de l'avis", "Ex. 27/05/2026", translatable=False),
                          "experience": text("Date de l'expérience", "Ex. 15 mai 2026"),
                      })),
    "mt-app": dict(display_name="Application", icon="block-mobile", color="#5a2a17", preview_field="name",
                   schema=plain({
                       "name": text("Nom", required=True), "text": area("Description"),
                       "app_store": link("Lien App Store"), "google_play": link("Lien Google Play"),
                       "more_label": text("Texte du lien", "Ex. Découvrir"), "more_link": link("Lien"),
                   })),
    "mt-rate-row": dict(display_name="Taux", icon="block-dollar-sign", color="#5a2a17", preview_field="rate",
                        schema=plain({
                            "duration": option("Durée", DURATIONS, "20"),
                            "profile": option("Profil", [("excellent", "Excellent"), ("tres-bon", "Très bon"), ("bon", "Bon")], "excellent"),
                            "rate": text("Taux (%)", "Ex. 3,35", required=True, translatable=False),
                            "trend": option("Tendance", [("stable", "Stable"), ("up", "En hausse"), ("down", "En baisse")], "stable"),
                        })),
}

NAV = {
    "mt-nav-link": dict(display_name="Lien de menu", icon="block-share", color="#b0a8a3", preview_field="label",
                        schema=plain({
                            "label": text("Texte", required=True),
                            "link": link("Lien"),
                            "highlight": boolean("Mettre en avant (bouton dans le menu)", "Ex. Je fais une simulation."),
                        })),
    "mt-nav-item": dict(display_name="Rubrique du menu", icon="block-share", color="#b0a8a3", preview_field="label",
                        schema=plain({
                            "label": area("Texte", "Entrée pour passer à la ligne, comme sur le site.", required=True),
                            "link": link("Lien", "Page d'accueil de la rubrique."),
                            "cta": bloks("Bouton en haut du menu", ["mt-button"], "Ex. Je fais une simulation de prêt immobilier.", maximum=1),
                            "columns": bloks("Colonnes du menu déroulant", ["mt-link-column"], "Jusqu'à 4 colonnes.", maximum=4),
                            "promo_image": media("Image du menu", videos=False),
                            "promo_title": text("Titre sur l'image"),
                            "promo_link": link("Lien de l'image"),
                        })),
    "mt-footer-column": dict(display_name="Colonne du pied de page", icon="block-table", color="#b0a8a3", preview_field="title",
                             schema=plain({"title": text("Titre"), "links": bloks("Liens", ["mt-nav-link"])})),
}

PAGES = {
    "mt-page": dict(display_name="Page libre", icon="block-doc", color="#302e2d", is_root=True, is_nestable=False,
                    description="Une page construite librement à partir des sections (accueil, Actualités, pages de campagne…).",
                    schema=plain({"body": None}, [SEO_TAB])),
    "mt-product-page": dict(display_name="Page produit", icon="block-locked", color="#c0543a", is_root=True, is_nestable=False,
                            description="Modèle verrouillé : un Hero, jusqu'à 20 sections de contenu, un appel à l'action final.",
                            schema=plain({
                                "product": option("Produit", CATEGORIES, "credit-immobilier",
                                                  "Sert au fil d'Ariane et aux actualités liées."),
                                "hero": None, "sections": None, "cta": None,
                            }, [SEO_TAB])),
    "mt-article": dict(display_name="Article d'actualité", icon="block-doc", color="#7a3419", is_root=True, is_nestable=False,
                       description="Un article de la rubrique Actualités.",
                       schema=plain({
                           "title": text("Titre", required=True),
                           "category": option("Thème", CATEGORIES, "credit-immobilier"),
                           "date": {"type": "datetime", "display_name": "Date de publication", "disable_time": True},
                           "excerpt": area("Chapeau", "1 à 2 phrases, affichées sur les cartes d'articles.", max_length=280),
                           "image": media("Image principale", videos=False),
                           "author": text("Auteur", translatable=False),
                           "author_role": text("Fonction de l'auteur"),
                           "reading_time": text("Temps de lecture", "Ex. 4 min", translatable=False),
                           "body": rich("Texte de l'article", long=True),
                           "after": None,
                       }, [SEO_TAB])),
    "mt-rates-config": dict(display_name="Barème des taux", icon="block-dollar-sign", color="#c0543a", is_root=True, is_nestable=False,
                            description="Les taux du moment, utilisés par tous les simulateurs, tuiles et tableaux du site.",
                            schema=plain({
                                "updated_on": {"type": "datetime", "display_name": "Taux au", "disable_time": True,
                                               "description": "Date affichée à côté des taux, ex. Taux moyen au 26/10/26."},
                                "rows": bloks("Taux par durée et profil", ["mt-rate-row"], "Une ligne par durée et par profil."),
                                "insurance_bank_rate": text("Taux d'assurance moyen en banque (%)", "Ex. 0,34", translatable=False),
                                "insurance_delegated_rate": text("Taux d'assurance en délégation (%)", "Ex. 0,10", translatable=False),
                                "consolidation_rate": text("Taux moyen du rachat de crédits (%)", "Ex. 5,40", translatable=False),
                            })),
    "mt-site-config": dict(display_name="Paramètres du site", icon="block-wallet", color="#b0a8a3", is_root=True, is_nestable=False,
                           description="En-tête, menu, pied de page et note Trustpilot pour tout le site.",
                           schema=plain({}, [
                               ("En-tête", {
                                   "logo": media("Logo", videos=False),
                                   "logo_mobile": media("Logo mobile (compact)", videos=False),
                                   "header_buttons": bloks("Boutons de l'en-tête", ["mt-button"], maximum=2),
                                   "nav": bloks("Menu", ["mt-nav-item"]),
                               }),
                               ("Trustpilot", {
                                   "tp_score": text("Note", "Ex. 4,8", translatable=False),
                                   "tp_count": text("Nombre d'avis", "Ex. 26 253", translatable=False),
                                   "tp_label": text("Libellé", "Ex. Excellent"),
                                   "tp_link": link("Lien vers les avis"),
                               }),
                               ("Sections communes", {
                                   "global_sections": bloks("Sections affichées en bas de toutes les pages",
                                                            ["mt-app-promo", "mt-alert", "mt-reviews", "mt-cta"],
                                                            "Ex. Applications mobiles et Vigilance fraude. Modifiées ici, elles changent partout."),
                               }),
                               ("Pied de page", {
                                   "footer_logo": media("Logo du pied de page", videos=False),
                                   "footer_columns": bloks("Colonnes", ["mt-footer-column"], "Jusqu'à 4 colonnes à côté de la newsletter.", maximum=4),
                                   "newsletter_title": text("Titre de la newsletter"),
                                   "newsletter_text": rich("Texte sous le champ e-mail"),
                                   "social_facebook": link("Facebook"), "social_linkedin": link("LinkedIn"),
                                   "social_youtube": link("YouTube"), "social_x": link("X (Twitter)"),
                                   "product_columns": bloks("Grandes colonnes de liens produits", ["mt-footer-column"], maximum=5),
                                   "legal_text": rich("Mention légale en bas de page", "Ex. Un crédit vous engage et doit être remboursé…"),
                                   "copyright": text("Copyright", "{year} devient l'année en cours."),
                               }),
                           ])),
}


def groups():
    want = ["Meilleurtaux · Sections", "Meilleurtaux · Éléments", "Meilleurtaux · Pages", "Meilleurtaux · Menu et paramètres"]
    have = {g["name"]: g["uuid"] for g in api("GET", "/component_groups/")["component_groups"]}
    for n in want:
        if n not in have:
            have[n] = api("POST", "/component_groups/", {"component_group": {"name": n}})["component_group"]["uuid"]
    return have


def main():
    g = groups()
    sec_uuid, item_uuid = g["Meilleurtaux · Sections"], g["Meilleurtaux · Éléments"]
    section_names = list(SECTIONS)
    body_field = {"type": "bloks", "display_name": "Sections", "description": "Cliquez sur + pour ajouter une section. Glissez pour réordonner.",
                  "restrict_type": "groups", "restrict_components": True, "component_group_whitelist": [sec_uuid, item_uuid]}
    PAGES["mt-page"]["schema"]["body"] = {**body_field, "pos": 0}
    ps = PAGES["mt-product-page"]["schema"]
    ps["hero"] = {**bloks("Hero", ["mt-hero"], "Exactement un Hero.", maximum=1, minimum=1), "pos": 1}
    ps["sections"] = {**bloks("Sections de contenu", [n for n in section_names if n != "mt-hero"],
                              "Jusqu'à 20 sections entre le Hero et l'appel à l'action.", maximum=20), "pos": 2}
    ps["cta"] = {**bloks("Appel à l'action final", ["mt-cta"], "Un seul.", maximum=1), "pos": 3}
    after = PAGES["mt-article"]["schema"]["after"]
    PAGES["mt-article"]["schema"]["after"] = {**bloks("Sections après l'article", ["mt-cta", "mt-news", "mt-simulator", "mt-card-grid"],
                                                      "Ex. un simulateur et les articles liés."), "pos": after["pos"] if after else 9}

    existing = {c["name"]: c for c in all_pages("/components/", "components")}
    failed = []
    for bucket, group, root, nestable in [(SECTIONS, "Meilleurtaux · Sections", False, True),
                                          (ITEMS, "Meilleurtaux · Éléments", False, True),
                                          (NAV, "Meilleurtaux · Menu et paramètres", False, True),
                                          (PAGES, "Meilleurtaux · Pages", True, False)]:
        for name, spec in bucket.items():
            grp = g["Meilleurtaux · Menu et paramètres"] if name in ("mt-site-config", "mt-rates-config") else g[group]
            comp = {
                "name": name, "display_name": spec["display_name"], "schema": spec["schema"],
                "is_root": spec.get("is_root", root), "is_nestable": spec.get("is_nestable", nestable),
                "component_group_uuid": grp, "icon": spec.get("icon"), "color": spec.get("color"),
                "preview_field": spec.get("preview_field"), "description": spec.get("description", ""),
            }
            try:
                if name in existing:
                    cur = existing[name]
                    for keep in ("image",):  # preset_id is never kept: no default presets
                        if cur.get(keep):
                            comp[keep] = cur[keep]
                    api("PUT", f"/components/{cur['id']}", {"component": comp})
                    print("updated", name)
                else:
                    api("POST", "/components/", {"component": comp})
                    print("created", name)
            except RuntimeError as e:
                print("FAILED", name, e, file=sys.stderr)
                failed.append(name)
    if failed:
        sys.exit(f"schema writes failed: {failed}")


if __name__ == "__main__":
    main()
