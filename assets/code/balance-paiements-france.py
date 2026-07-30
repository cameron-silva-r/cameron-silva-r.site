"""Balance des paiements de la France : compte courant, biens, services,
revenus - d'ou vient le solde exterieur et comment a-t-il bouge depuis 2010 ?

Script utilise pour la note "Balance des paiements : la France vit-elle
au-dessus de ses moyens ?" (cameron-silva.fr/blog/balance-paiements-france.html).

Sources (API publique Eurostat, sans cle) :
- bop_c6_a   : balance des paiements annuelle (BPM6), par poste, vis-a-vis
  du reste du monde (partner=WRL_REST), solde (stk_flow=BAL).
- nama_10_gdp : PIB nominal, pour exprimer chaque poste en % du PIB.
"""

import requests

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

BOP_LABELS = {
    "CA": "Compte courant (solde global)",
    "G": "Biens",
    "S": "Services",
    "IN1": "Revenu primaire (salaires, interets, dividendes)",
    "IN2": "Revenu secondaire (transferts courants)",
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
    """Deroule un JSON-stat a une seule dimension "libre" (ex: time)
    vers un dict {libelle_categorie: valeur}."""
    dims = payload["id"]
    sizes = payload["size"]
    cats = payload["dimension"][dim_name]["category"]["index"]
    pos = dims.index(dim_name)
    stride = 1
    for s in sizes[pos + 1:]:
        stride *= s
    values = payload["value"]
    return {code: values.get(str(idx * stride)) for code, idx in cats.items()}


def pib_nominal(depuis=2010):
    """PIB nominal (millions d'euros), FR, depuis une annee donnee."""
    payload = _fetch(
        "nama_10_gdp", geo="FR", na_item="B1GQ", unit="CP_MEUR",
        sinceTimePeriod=depuis,
    )
    return _to_series(payload, "time")


def balance_par_poste(depuis=2010):
    """Solde de chaque poste de la balance des paiements (millions d'euros),
    FR vis-a-vis du reste du monde, par annee."""
    result = {}
    for bop_item in BOP_LABELS:
        payload = _fetch(
            "bop_c6_a", geo="FR", partner="WRL_REST", sector10="S1",
            sectpart="S1", stk_flow="BAL", currency="MIO_EUR",
            bop_item=bop_item, sinceTimePeriod=depuis,
        )
        result[bop_item] = _to_series(payload, "time")
    return result


def en_pct_pib(series_meur, pib):
    """Convertit un dict {annee: millions d'euros} en % du PIB de la meme annee."""
    out = {}
    for annee, valeur in series_meur.items():
        gdp = pib.get(annee)
        if valeur is not None and gdp:
            out[annee] = round(100 * valeur / gdp, 2)
    return out


if __name__ == "__main__":
    pib = pib_nominal()
    postes = balance_par_poste()

    postes_pct = {code: en_pct_pib(serie, pib) for code, serie in postes.items()}
    annees = sorted(pib.keys())

    print("Balance des paiements de la France, % du PIB, 2010-2025")
    header = "Annee".ljust(7) + "".join(code.ljust(8) for code in BOP_LABELS)
    print(header)
    for annee in annees:
        row = annee.ljust(7)
        for code in BOP_LABELS:
            val = postes_pct[code].get(annee)
            row += (f"{val:>6.2f} " if val is not None else "   n/a ")
        print(row)

    # Verification interne : CA doit etre proche de G + S + IN1 + IN2
    print("\nVerification (CA vs somme des composantes), points de % de PIB :")
    for annee in annees:
        ca = postes_pct["CA"].get(annee)
        somme = sum(
            postes_pct[c].get(annee, 0) or 0 for c in ["G", "S", "IN1", "IN2"]
        )
        if ca is not None:
            print(f"  {annee} : CA={ca:.2f}  somme composantes={somme:.2f}")
