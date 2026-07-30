"""Financement de l'adaptation climatique : la profondeur du systeme
financier attenue-t-elle le lien entre exposition climatique et cout de la
dette publique ?

Etude inspiree du "Papier 3" d'un projet de these sur risques climatiques
physiques, resilience economique et financement de l'adaptation (qui porte,
lui, sur des donnees de credit d'entreprise non disponibles publiquement).
Utilise pour la note "Financer l'adaptation climatique : ce que suggèrent
les donnees macro" (cameron-silva.fr/blog/financement-adaptation-climatique.html).

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
DEPTH_INDICATOR = "FD.AST.PRVT.GD.ZS"     # credit prive interieur, % PIB
COST_INDICATOR = "GC.XPN.INTP.RV.ZS"      # interets payes, % des recettes publiques


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
    profondeur = fetch_indicator(DEPTH_INDICATOR, iso3_codes)
    cout_dette = fetch_indicator(COST_INDICATOR, iso3_codes)

    communs = set(exposition) & set(profondeur) & set(cout_dette)
    rows = sorted(communs, key=lambda k: exposition[k], reverse=True)

    print("Pays classes par exposition climatique physique (0-100) :")
    for iso3 in rows:
        print(
            f"  {COUNTRIES[iso3]:<18} exposition={exposition[iso3]:>5.1f}  "
            f"credit_prive_%pib={profondeur[iso3]:>6.1f}  "
            f"interets_%recettes={cout_dette[iso3]:>5.1f}"
        )

    mediane_profondeur = statistics.median(profondeur[k] for k in communs)
    profond = [k for k in communs if profondeur[k] >= mediane_profondeur]
    superficiel = [k for k in communs if profondeur[k] < mediane_profondeur]

    def correl(groupe):
        x = [exposition[k] for k in groupe]
        y = [cout_dette[k] for k in groupe]
        return stats.pearsonr(x, y)

    r_all, p_all = correl(communs)
    r_profond, p_profond = correl(profond)
    r_superficiel, p_superficiel = correl(superficiel)

    print(f"\nCorrelation exposition / cout de la dette, ensemble du panel (n={len(communs)}) : r={r_all:.2f} (p={p_all:.3f})")
    print(f"  Systeme financier profond (n={len(profond)})     : r={r_profond:.2f} (p={p_profond:.3f}) -> {[COUNTRIES[k] for k in profond]}")
    print(f"  Systeme financier superficiel (n={len(superficiel)}) : r={r_superficiel:.2f} (p={p_superficiel:.3f}) -> {[COUNTRIES[k] for k in superficiel]}")
