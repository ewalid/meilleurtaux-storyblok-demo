"""Download Meilleurtaux imagery from the public site, upload to the Storyblok asset
library (idempotent by filename), write assets/manifest.json {key: {filename, alt}}."""
import json
import mimetypes
import os
import subprocess
import sys
import urllib.request
import uuid

from sb import api, all_pages

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("BT_ASSET_CACHE", "/tmp/mt-assets")
os.makedirs(CACHE, exist_ok=True)

ASSETS = {
    "logo": ("https://www.meilleurtaux.com/images_html/new-logo-mtx.svg", "Meilleurtaux", "mt-logo.svg"),
    "logo_m": ("https://www.meilleurtaux.com/images_html/new-logo-mtx-m.svg", "Meilleurtaux", "mt-logo-m.svg"),
    "tp_logo": ("https://www.meilleurtaux.com/images_html/TP_logo.svg", "Trustpilot", "trustpilot-logo.svg"),
    "tp_logo_white": ("https://www.meilleurtaux.com/images_html/TP_logowhite.svg", "Trustpilot", "trustpilot-logo-white.svg"),
    "app_store": ("https://www.meilleurtaux.com/images_html/homepage-new-v2/img/btn-app-store.png", "Télécharger dans l'App Store", "btn-app-store.png"),
    "google_play": ("https://www.meilleurtaux.com/images_html/homepage-new-v2/img/btn-google-play.png", "Disponible sur Google Play", "btn-google-play.png"),
    "app_phones": ("https://www.meilleurtaux.com/images_html/homepage-new-v2/img/app.png", "Applications Meilleurtaux sur smartphone", "app-meilleurtaux.png"),
    "mega_immo": ("https://www.meilleurtaux.com/images_html/mega-menu/bg_immo.webp", "Couple devant sa nouvelle maison", "mega-menu-immo.webp"),
    "mega_ade": ("https://www.meilleurtaux.com/images_html/mega-menu/ade-banner.webp", "Assurance de prêt", "mega-menu-ade.webp"),
    "ico_ci": ("https://www.meilleurtaux.com/images_html/home_hp/ci.svg", "Crédit immobilier", "ico-credit-immobilier.svg"),
    "ico_adp": ("https://www.meilleurtaux.com/images_html/home_hp/assurance-pi.svg", "Assurance de prêt immobilier", "ico-assurance-pret.svg"),
    "ico_vie": ("https://www.meilleurtaux.com/images_html/home_hp/assurance-vie.svg", "Assurance vie", "ico-assurance-vie.svg"),
    "ico_rac": ("https://www.meilleurtaux.com/images_html/home_hp/rac.svg", "Rachat de crédit", "ico-rachat-credit.svg"),
    "ico_cc": ("https://www.meilleurtaux.com/images_html/home_hp/cc.svg", "Crédit à la consommation", "ico-credit-conso.svg"),
    "ico_auto": ("https://www.meilleurtaux.com/images_html/home_hp/assurance-auto.svg", "Assurance auto", "ico-assurance-auto.svg"),
    "ico_habitation": ("https://www.meilleurtaux.com/images_html/home_hp/assurance-habitation.svg", "Assurance habitation", "ico-assurance-habitation.svg"),
    "ico_ci2": ("https://www.meilleurtaux.com/images_html/home_hp/ci-2.svg", "Crédit immobilier", "ico-guide-credit-immobilier.svg"),
    "ico_rac2": ("https://www.meilleurtaux.com/images_html/home_hp/rac-2.svg", "Rachat de crédits", "ico-guide-rachat.svg"),
    "ico_cc2": ("https://www.meilleurtaux.com/images_html/home_hp/cc-2.svg", "Crédit consommation", "ico-guide-conso.svg"),
    "ico_hab2": ("https://www.meilleurtaux.com/images_html/home_hp/assurance-habitation-2.svg", "Assurance de biens", "ico-guide-biens.svg"),
    "ico_adp3": ("https://www.meilleurtaux.com/images_html/home_hp/assurance-pi-3.svg", "Assurance de prêt", "ico-guide-assurance-pret.svg"),
    "ico_vie2": ("https://www.meilleurtaux.com/images_html/home_hp/assurance-vie-2.svg", "Assurance de personnes", "ico-guide-personnes.svg"),
    "ico_info_ci": ("https://www.meilleurtaux.com/images_html/home_hp/section-assurance-infos/ico-ci.svg", "Crédit immobilier", "ico-info-credit-immobilier.svg"),
    "ico_info_ade": ("https://www.meilleurtaux.com/images_html/home_hp/section-assurance-infos/ico-ade.svg", "Assurance emprunteur", "ico-info-assurance-emprunteur.svg"),
    "ico_info_rac": ("https://www.meilleurtaux.com/images_html/home_hp/section-assurance-infos/ico-rac.svg", "Rachat de crédit", "ico-info-rachat.svg"),
    "promo_vie": ("https://www.meilleurtaux.com/images/homepage/bloc-a-la-une/offre_essentiel_vie-3.webp", "Paysage de montagne au lever du soleil", "offre-assurance-vie.webp"),
    "elysee": ("https://www.meilleurtaux.com/images/homepage/home-presidentiel.webp", "Palais de l'Élysée", "observatoire-elysee.webp"),
    "agence": ("https://www.meilleurtaux.com/images_html/home_hp/agence-img.webp", "Conseillère Meilleurtaux en agence", "agence-meilleurtaux.webp"),
    "pdv_conso": ("https://www.meilleurtaux.com/images_html/carrousel-pdv-hp/credit-conso.webp", "Couple heureux dans sa nouvelle voiture", "projet-credit-conso.webp"),
    "pdv_habitation": ("https://www.meilleurtaux.com/images_html/carrousel-pdv-hp/assu-habitation.webp", "Famille dans son nouveau logement", "projet-assurance-habitation.webp"),
    "pdv_sante": ("https://www.meilleurtaux.com/images_html/carrousel-pdv-hp/assu-sante.webp", "Homme souriant", "projet-mutuelle-sante.webp"),
    "pdv_auto": ("https://www.meilleurtaux.com/images_html/carrousel-pdv-hp/assu-auto.webp", "Femme au volant", "projet-assurance-auto.webp"),
    "pdv_rac": ("https://www.meilleurtaux.com/images_html/carrousel-pdv-hp/rac.webp", "Couple qui fait ses comptes", "projet-rachat-credit.webp"),
    "rejoindre": ("https://www.meilleurtaux.com/images_html/home_hp/nous_rejoindre_desktop.webp", "L'équipe Meilleurtaux au bureau", "nous-rejoindre.webp"),
    "hero_ci": ("https://www.meilleurtaux.com/images/assurance/home/credit-immo/hero-home-immo_2x.webp", "Couple qui consulte une simulation sur tablette", "hero-credit-immobilier.webp"),
    "cas_marc": ("https://www.meilleurtaux.com/images/assurance/home/credit-immo/MarcSophie.webp", "Marc et Sophie", "cas-marc-sophie.webp"),
    "cas_julie": ("https://www.meilleurtaux.com/images/assurance/home/credit-immo/JulieThomas.webp", "Julie et Thomas", "cas-julie-thomas.webp"),
    "prof_secundo": ("https://www.meilleurtaux.com/images/assurance/home/credit-immo/Les%20secundo-accedants.webp", "Famille dans son salon", "profil-secundo-accedants.webp"),
    "prof_emploi": ("https://www.meilleurtaux.com/images/assurance/home/credit-immo/Les%20demandeurs%20demploi.webp", "Femme souriante", "profil-demandeurs-emploi.webp"),
    "prof_auto": ("https://www.meilleurtaux.com/images/assurance/home/credit-immo/Les%20auto-entrepreneurs.webp", "Auto-entrepreneur au travail", "profil-auto-entrepreneurs.webp"),
    "prof_seniors": ("https://www.meilleurtaux.com/images/assurance/home/credit-immo/Les%20seniors.webp", "Couple de seniors", "profil-seniors.webp"),
    "prof_primo": ("https://www.meilleurtaux.com/images/assurance/home/credit-immo/Les%20primo-accedants.webp", "Jeune couple dans son premier logement", "profil-primo-accedants.webp"),
    "signature": ("https://www.meilleurtaux.com/images/assurance/home/credit-immo/signature-contrat.webp", "Un conseiller explique un contrat de prêt immobilier", "signature-contrat.webp"),
    "contrat": ("https://www.meilleurtaux.com/images/assurance/home/credit-immo/contrat.webp", "Signature d'un contrat de prêt immobilier", "contrat-pret.webp"),
    "expert_ci": ("https://www.meilleurtaux.com/images/Guillaume-Fourt.webp", "Expert crédit immobilier", "expert-credit-immobilier.webp"),
    "hero_adp": ("https://www.meilleurtaux.com/images/ADE%20revamp/iStock-femme-hero-image.png", "Femme souriante qui économise sur son assurance", "hero-assurance-pret.png"),
    "cas_clarysse": ("https://www.meilleurtaux.com/images/ADE%20revamp/iStock-couple%20souriant%20exemple.png", "Clarysse et Gabriel", "cas-clarysse-gabriel.png"),
    "cas_francesco": ("https://www.meilleurtaux.com/images/ADE%20revamp/iStock-couple-souriant.png", "Francesco et Emilie", "cas-francesco-emilie.png"),
    "cas_pierre": ("https://www.meilleurtaux.com/images/ADE%20revamp/iStock-homme-souriant-exemple.png", "Pierre", "cas-pierre.png"),
    "adp_phone": ("https://www.meilleurtaux.com/images/ADE%20revamp/IMG-femme-recherche_telephone_ade.png", "Femme qui compare son assurance sur smartphone", "assurance-smartphone.png"),
    "adp_couple": ("https://www.meilleurtaux.com/images/ADE%20revamp/Couple-recherche-ade.png", "Couple qui discute d'assurance emprunteur", "assurance-couple.png"),
    "hero_rac": ("https://www.meilleurtaux.com/images/rac/HomeRAC/heroRac.webp", "Regroupez vos prêts en une seule mensualité", "hero-rachat-credit.webp"),
    "cas_natacha": ("https://www.meilleurtaux.com/images/rac/HomeRAC/cas_de_natacha.webp", "Natacha", "cas-natacha.webp"),
    "cas_marie": ("https://www.meilleurtaux.com/images/rac/HomeRAC/cas_de_marie_et_stanislas.webp", "Marie et Stanislas", "cas-marie-stanislas.webp"),
    "rac_plusieurs": ("https://www.meilleurtaux.com/images/rac/HomeRAC/personnes_a_plusieurs_credits.webp", "Personne avec plusieurs crédits", "profil-plusieurs-credits.webp"),
    "rac_projet": ("https://www.meilleurtaux.com/images/rac/HomeRAC/emprunteurs__nouveau_projet.webp", "Emprunteurs avec un nouveau projet", "profil-nouveau-projet.webp"),
    "rac_sans": ("https://www.meilleurtaux.com/images/rac/HomeRAC/sans_difficulte_financiere.webp", "Profils sans difficulté financière", "profil-sans-difficulte.webp"),
    "rac_avantages": ("https://www.meilleurtaux.com/images/rac/HomeRAC/avantages_du_regroupement.webp", "Un homme consulte des documents", "avantages-regroupement.webp"),
    "rac_conseiller": ("https://www.meilleurtaux.com/images/rac/HomeRAC/conseiller_financier.webp", "Conseiller financier aidant un client", "conseiller-financier.webp"),
    "actu_rac": ("https://www.meilleurtaux.com/images/actu/2026/2026102714-rachat-credits-banques-selection-taux.webp", "Dossiers de crédit et calculatrice sur une table", "actu-rachat-credits-banques.webp"),
    "actu_mutuelle": ("https://www.meilleurtaux.com/images/actu/2026/2026102311_mutuelle-gel-censure-conseil-constitutionnel.webp", "Document de mutuelle santé et loupe", "actu-mutuelle-gel.webp"),
    "actu_tempete": ("https://www.meilleurtaux.com/images/actu/2026/2026102311-tempete-austen-assurance-habitation.webp", "Dégâts de tempête sur des maisons", "actu-tempete-assurance-habitation.webp"),
    "actu_oat": ("https://www.meilleurtaux.com/images/actu/2026/2026102113_oat-10ans-credit-immobilier.webp", "Dossier de prêt immobilier et calculatrice", "actu-oat-credit-immobilier.webp"),
    "actu_taux": ("https://www.meilleurtaux.com/images/actu/2026/2026101514-credit-immobilier-taux-durees.webp", "Couple en banque examinant un dossier de crédit", "actu-taux-durees.webp"),
    "actu_ade": ("https://www.meilleurtaux.com/images/actu/2026/2026101514_credit-immo-assurance-emprunteur-2026.webp", "Dossier de prêt immobilier et documents d'assurance", "actu-assurance-emprunteur-2026.webp"),
    "actu_ptz": ("https://www.meilleurtaux.com/images/actu/2026/2026100111-ptz-parentalite-plf2027.webp", "Jeunes parents préparant un projet logement", "actu-ptz-parentalite.webp"),
    "actu_arnaque": ("https://www.meilleurtaux.com/images/actu/2026/2026101515-credit-immobilier-arnaque-faux-courtier.webp", "Personne vérifiant une offre de prêt", "actu-arnaque-faux-courtier.webp"),
    "bank_caisse-epargne": ("https://www.meilleurtaux.com/images_html/carrousel-bnq/caisse-epargne.svg", "Caisse d'Epargne", "banque-caisse-epargne.svg"),
    "bank_bnp": ("https://www.meilleurtaux.com/images_html/carrousel-bnq/bnp.svg", "BNP Paribas", "banque-bnp.svg"),
    "bank_ca": ("https://www.meilleurtaux.com/images_html/carrousel-bnq/ca.svg", "Crédit Agricole", "banque-ca.svg"),
    "bank_lbp": ("https://www.meilleurtaux.com/images_html/carrousel-bnq/lbp.svg", "La Banque Postale", "banque-lbp.svg"),
    "bank_hellobank": ("https://www.meilleurtaux.com/images_html/carrousel-bnq/hellobank.svg", "Hello bank!", "banque-hellobank.svg"),
    "bank_sofinco": ("https://www.meilleurtaux.com/images_html/carrousel-bnq/sofinco.svg", "Sofinco", "banque-sofinco.svg"),
    "bank_sbe": ("https://www.meilleurtaux.com/images_html/carrousel-bnq/sbe.svg", "Banque Populaire", "banque-sbe.svg"),
    "bank_cashper": ("https://www.meilleurtaux.com/images_html/carrousel-bnq/cashper.svg", "Cashper", "banque-cashper.svg"),
    "bank_fortuneo": ("https://www.meilleurtaux.com/images_html/carrousel-bnq/fortuneo.svg", "Fortuneo", "banque-fortuneo.svg"),
    "bank_sg": ("https://www.meilleurtaux.com/images_html/carrousel-bnq/sg.svg", "Société Générale", "banque-sg.svg"),
    "ins_maif": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_Maif.webp", "Maif", "assureur-maif.webp"),
    "ins_malakoff": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_Malakoff.webp", "Malakoff", "assureur-malakoff.webp"),
    "ins_metlife": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_MetLife.webp", "MetLife", "assureur-metlife.webp"),
    "ins_swisslife": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_SwissLife.webp", "SwissLife", "assureur-swisslife.webp"),
    "ins_thelem": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_Thelem.webp", "Thelem", "assureur-thelem.webp"),
    "ins_april": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_April.webp", "April", "assureur-april.webp"),
    "ins_axa": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_Axa.webp", "Axa", "assureur-axa.webp"),
    "ins_cardif": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_Cardif.webp", "Cardif", "assureur-cardif.webp"),
    "ins_cnp": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_CNP.webp", "CNP", "assureur-cnp.webp"),
    "ins_generali": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_Generali.webp", "Generali", "assureur-generali.webp"),
    "ins_harmonie": ("https://www.meilleurtaux.com/images/ADE%20revamp/LOGOS/Logo_Harmonie.webp", "Harmonie", "assureur-harmonie.webp"),
}

def folder_id():
    for f in api("GET", "/asset_folders/").get("asset_folders", []):
        if f["name"] == "Meilleurtaux":
            return f["id"]
    return api("POST", "/asset_folders/", {"asset_folder": {"name": "Meilleurtaux"}})["asset_folder"]["id"]


def fetch(url, dest):
    if not os.path.exists(dest):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
            f.write(r.read())
    # Large rasters: shrink to 1800px wide to keep the CDN light.
    if dest.lower().endswith((".png", ".jpg", ".jpeg")) and os.path.getsize(dest) > 1_500_000:
        subprocess.run(["sips", "-Z", "1800", dest], capture_output=True)
    return dest


def upload(path, filename, fid, alt):
    size = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path], capture_output=True, text=True).stdout
    w = h = None
    for line in size.splitlines():
        if "pixelWidth" in line:
            w = line.split()[-1]
        if "pixelHeight" in line:
            h = line.split()[-1]
    body = {"filename": filename, "asset_folder_id": fid}
    if w and h and not filename.endswith(".svg"):
        body["size"] = f"{w}x{h}"
    signed = api("POST", "/assets/", body)
    fields = signed["fields"]
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: {ctype}\r\n\r\n".encode())
    parts.append(open(path, "rb").read())
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    req = urllib.request.Request(signed["post_url"], data=b"".join(parts), method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    urllib.request.urlopen(req).read()
    api("GET", f"/assets/{signed['id']}/finish_upload")
    api("PUT", f"/assets/{signed['id']}", {"asset": {"alt": alt, "title": alt}})
    return api("GET", f"/assets/{signed['id']}")


def main():
    fid = folder_id()
    existing = {a["filename"].rsplit("/", 1)[-1].lower(): a for a in all_pages("/assets/?in_folder=%d" % fid, "assets")}
    manifest_path = os.path.join(HERE, "assets", "manifest.json")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    manifest = {}
    for key, (url, alt, filename) in ASSETS.items():
        name = filename.lower()
        a = existing.get(name)
        if not a:
            try:
                local = fetch(url, os.path.join(CACHE, filename))
                a = upload(local, filename, fid, alt)
                print("uploaded", key)
            except Exception as e:  # keep going; report at the end
                print("FAILED", key, e, file=sys.stderr)
                continue
        manifest[key] = {"id": a["id"], "filename": a["filename"].replace("s3.amazonaws.com/", ""), "alt": alt}
    json.dump(manifest, open(manifest_path, "w"), indent=2)
    open(manifest_path, "a").write("\n")
    print(len(manifest), "assets in manifest")


if __name__ == "__main__":
    main()
