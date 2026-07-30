"""Deficit public francais : d'ou vient-il, quels comptes sont deficitaires,
recettes ou depenses ?

Script utilise pour la note "Deficit public et donnees : ce que mesurent
(vraiment) les chiffres" (cameron-silva.fr/blog/deficit-public-et-donnees.html).

Sources (API publique Eurostat, sans cle) :
- gov_10a_main : recettes, depenses et solde des administrations publiques
  (notification SEC 2010), par sous-secteur (Etat, collectivites locales,
  securite sociale).
- gov_10a_exp  : depenses publiques par fonction (COFOG).
"""

import requests

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

SUBSECTOR_LABELS = {
    "S13": "Toutes administrations publiques",
    "S1311": "Etat (administration centrale)",
    "S1313": "Collectivites locales",
    "S1314": "Securite sociale",
}

COFOG_LABELS = {
    "GF01": "Services generaux des administrations publiques",
    "GF02": "Defense",
    "GF03": "Ordre et securite publics",
    "GF04": "Affaires economiques",
    "GF05": "Protection de l'environnement",
    "GF06": "Logement et equipements collectifs",
    "GF07": "Sante",
    "GF08": "Loisirs, culture et culte",
    "GF09": "Enseignement",
    "GF10": "Protection sociale",
}


def _fetch(dataset, **params):
    """Interroge l'API Eurostat (format JSON-stat) et renvoie le JSON brut."""
    query = "&".join(
        f"{key}={v}" for key, values in params.items()
        for v in (values if isinstance(values, list) else [values])
    )
    url = f"{BASE}/{dataset}?format=JSON&{query}"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.json()


def _to_series(payload, dim_name):
    """Deroule un JSON-stat a une seule dimension "libre" (ex: time ou sector)
    vers un dict {libelle_categorie: valeur}."""
    dims = payload["id"]
    sizes = payload["size"]
    cats = payload["dimension"][dim_name]["category"]["index"]
    # position (0-based) de la dimension libre dans l'ordre des dimensions
    pos = dims.index(dim_name)
    stride = 1
    for s in sizes[pos + 1:]:
        stride *= s
    values = payload["value"]
    out = {}
    for code, idx in cats.items():
        out[code] = values.get(str(idx * stride))
    return out


def deficit_par_annee():
    """Solde nominal (B9), recettes (TR) et depenses (TE) totales, % PIB, FR."""
    result = {}
    for na_item in ["B9", "TR", "TE", "D41PAY"]:
        payload = _fetch(
            "gov_10a_main", geo="FR", sector="S13", unit="PC_GDP", na_item=na_item
        )
        result[na_item] = _to_series(payload, "time")
    return result


def deficit_par_sous_secteur(annees):
    """Solde (B9), % PIB, par sous-secteur d'administration publique, FR."""
    payload = _fetch(
        "gov_10a_main",
        geo="FR",
        sector=["S1311", "S1313", "S1314"],
        unit="PC_GDP",
        na_item="B9",
        time=annees,
    )
    dims, sizes = payload["id"], payload["size"]
    sector_idx = payload["dimension"]["sector"]["category"]["index"]
    time_idx = payload["dimension"]["time"]["category"]["index"]
    sector_pos, time_pos = dims.index("sector"), dims.index("time")
    sector_stride = 1
    for s in sizes[sector_pos + 1:]:
        sector_stride *= s
    time_stride = 1
    for s in sizes[time_pos + 1:]:
        time_stride *= s
    values = payload["value"]
    out = {}
    for sector, s_i in sector_idx.items():
        out[sector] = {}
        for year, t_i in time_idx.items():
            flat = s_i * sector_stride + t_i * time_stride
            out[sector][year] = values.get(str(flat))
    return out


def depenses_par_fonction(annee):
    """Depenses publiques par fonction (COFOG), % PIB, FR, une annee donnee."""
    payload = _fetch(
        "gov_10a_exp",
        geo="FR",
        sector="S13",
        unit="PC_GDP",
        na_item="TE",
        time=annee,
        cofog99=list(COFOG_LABELS.keys()),
    )
    series = _to_series(payload, "cofog99")
    return {COFOG_LABELS[code]: val for code, val in series.items()}


if __name__ == "__main__":
    agg = deficit_par_annee()
    print("Solde / recettes / depenses, % PIB, France (SEC 2010, notification Eurostat) :")
    for year in ["2019", "2020", "2021", "2022", "2023", "2024", "2025"]:
        print(
            f"  {year} : solde={agg['B9'].get(year)}  recettes={agg['TR'].get(year)}"
            f"  depenses={agg['TE'].get(year)}  interets={agg['D41PAY'].get(year)}"
        )

    print("\nSolde par sous-secteur, % PIB, France :")
    sous_secteurs = deficit_par_sous_secteur(
        ["2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    )
    for sector, values in sous_secteurs.items():
        print(f"  {SUBSECTOR_LABELS[sector]} : {values}")

    print("\nDepenses par fonction (COFOG), % PIB, France, 2023 :")
    for fonction, valeur in sorted(
        depenses_par_fonction("2023").items(), key=lambda kv: kv[1] or 0, reverse=True
    ):
        print(f"  {fonction} : {valeur}")
