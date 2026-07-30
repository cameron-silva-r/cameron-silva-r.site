"""Chaines de valeur et risque climatique : les economies exposees ET tres
ouvertes au commerce ont-elles des flux d'exportation plus instables ?

Etude inspiree du "Papier 2" d'un projet de these sur risques climatiques
physiques, resilience economique et financement de l'adaptation (qui porte,
lui, sur les chaines fournisseur-client au niveau des entreprises, avec des
donnees firm-to-firm non disponibles publiquement). Utilise pour la note
"Chaines de valeur face au risque climatique : une illustration macro"
(cameron-silva.fr/blog/chaines-valeur-climat.html).

Source : Banque mondiale, World Development Indicators (API REST, sans cle).
"""

import statistics
import requests
from scipy import stats

COUNTRIES = {
    "FRA": "France", "DEU": "Allemagne", "ESP": "Espagne", "ITA": "Italie",
    "POL": "Pologne", "ROU": "Roumanie", "GBR": "Royaume-Uni", "MAR": "Maroc",
    "ZAF": "Afrique du Sud", "TUR": "Turquie", "SAU": "Arabie saoudite",
    "CHN": "Chine", "IND": "Inde", "USA": "États-Unis", "BRA": "Brésil",
    "MEX": "Mexique", "CAN": "Canada", "BGD": "Bangladesh",
    "PHL": "Philippines", "KEN": "Kenya",
}

EXPOSURE_INDICATORS = ["EN.POP.EL5M.ZS", "EN.CLC.MDAT.ZS"]


def fetch_indicator(code, iso3_codes, mrv=6):
    url = (
        f"https://api.worldbank.org/v2/country/{';'.join(iso3_codes)}"
        f"/indicator/{code}?format=json&per_page=1000&mrv={mrv}"
    )
    data = requests.get(url, timeout=20).json()
    rows = sorted(data[1], key=lambda r: r["date"], reverse=True)
    out = {}
    for row in rows:
        iso3 = row["countryiso3code"]
        if iso3 not in out and row["value"] is not None:
            out[iso3] = float(row["value"])
    return out


def fetch_export_volatility(iso3_codes, years=15):
    """Ecart-type de la croissance des exportations de biens et services sur
    les `years` dernieres annees disponibles (instabilite des flux commerciaux)."""
    url = (
        f"https://api.worldbank.org/v2/country/{';'.join(iso3_codes)}"
        f"/indicator/NE.EXP.GNFS.KD.ZG?format=json&per_page=1000&mrv={years}"
    )
    data = requests.get(url, timeout=20).json()
    by_country = {}
    for row in data[1]:
        if row["value"] is not None:
            by_country.setdefault(row["countryiso3code"], []).append(float(row["value"]))
    return {iso3: statistics.stdev(v) for iso3, v in by_country.items() if len(v) >= 5}


def minmax(values):
    lo, hi = min(values.values()), max(values.values())
    if hi == lo:
        return {k: 50.0 for k in values}
    return {k: 100 * (v - lo) / (hi - lo) for k, v in values.items()}


def build_index(iso3_codes, codes):
    raw = {code: fetch_indicator(code, iso3_codes) for code in codes}
    common = set.intersection(*[set(d.keys()) for d in raw.values()])
    normalized = {code: minmax({k: v for k, v in d.items() if k in common})
                  for code, d in raw.items()}
    return {iso3: statistics.mean(normalized[code][iso3] for code in codes)
            for iso3 in common}


if __name__ == "__main__":
    iso3_codes = list(COUNTRIES.keys())

    exposition = build_index(iso3_codes, EXPOSURE_INDICATORS)
    imports = fetch_indicator("NE.IMP.GNFS.ZS", iso3_codes)
    exports = fetch_indicator("NE.EXP.GNFS.ZS", iso3_codes)
    volatilite = fetch_export_volatility(iso3_codes)

    communs = set(exposition) & set(imports) & set(exports) & set(volatilite)
    ouverture = {k: (imports[k] + exports[k]) / 2 for k in communs}
    ouverture_norm = minmax(ouverture)
    exposition_norm = {k: exposition[k] for k in communs}  # deja 0-100
    interaction = {k: exposition_norm[k] * ouverture_norm[k] / 100 for k in communs}

    rows = sorted(communs, key=lambda k: exposition[k], reverse=True)
    print("Pays classes par exposition climatique physique (0-100) :")
    for iso3 in rows:
        print(
            f"  {COUNTRIES[iso3]:<18} exposition={exposition[iso3]:>5.1f}  "
            f"ouverture_commerciale_%pib={ouverture[iso3]:>5.1f}  "
            f"volatilite_export={volatilite[iso3]:>5.2f}"
        )

    x_exp = [exposition_norm[k] for k in communs]
    x_ouv = [ouverture_norm[k] for k in communs]
    x_int = [interaction[k] for k in communs]
    y = [volatilite[k] for k in communs]

    r1, p1 = stats.pearsonr(x_exp, y)
    r2, p2 = stats.pearsonr(x_ouv, y)
    r3, p3 = stats.pearsonr(x_int, y)

    print(f"\nCorrelation exposition climatique seule / volatilite export : r={r1:.2f} (p={p1:.3f})")
    print(f"Correlation ouverture commerciale seule / volatilite export  : r={r2:.2f} (p={p2:.3f})")
    print(f"Correlation exposition x ouverture (interaction) / volatilite export : r={r3:.2f} (p={p3:.3f})")
