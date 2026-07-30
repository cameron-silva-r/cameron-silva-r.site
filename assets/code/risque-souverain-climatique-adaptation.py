"""Risque souverain climatique et adaptation publique : les marches / les
budgets font-ils une difference entre pays exposes-mais-adaptes et pays
exposes-et-non-adaptes ?

Etude inspiree du "Papier 1" d'un projet de these sur risques climatiques
physiques, resilience economique et financement de l'adaptation. Utilise pour
la note "Risque souverain climatique : l'adaptation publique change-t-elle
la donne ?" (cameron-silva.fr/blog/risque-souverain-climatique-adaptation.html).

Source : Banque mondiale, World Development Indicators + Worldwide
Governance Indicators (API REST, sans cle).

Limite assumee : cette etude utilise des donnees macro publiques (pas de
spreads souverains ni de donnees de marche obligataire, non accessibles
gratuitement) ; le cout de la dette est approxime par la part des recettes
publiques absorbee par le paiement des interets.
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

# Exposition climatique physique (0-100)
EXPOSURE_INDICATORS = ["EN.POP.EL5M.ZS", "EN.CLC.MDAT.ZS"]
# Capacite d'adaptation publique : reserves de change + efficacite de l'Etat
ADAPTATION_INDICATORS = ["FI.RES.TOTL.MO", "GOV_WGI_GE.EST"]
# Cout budgetaire de la dette (proxy du risque souverain "realise")
COST_INDICATOR = "GC.XPN.INTP.RV.ZS"  # interets payes, % des recettes publiques


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
    adaptation = build_index(iso3_codes, ADAPTATION_INDICATORS)
    cout_dette = fetch_indicator(COST_INDICATOR, iso3_codes)

    communs = set(exposition) & set(adaptation) & set(cout_dette)
    rows = sorted(communs, key=lambda k: exposition[k], reverse=True)

    print("Pays classes par exposition climatique physique (0-100) :")
    for iso3 in rows:
        print(
            f"  {COUNTRIES[iso3]:<18} exposition={exposition[iso3]:>5.1f}  "
            f"adaptation={adaptation[iso3]:>5.1f}  "
            f"interets_%recettes={cout_dette[iso3]:>5.1f}"
        )

    mediane_adapt = statistics.median(adaptation[k] for k in communs)
    forte = [k for k in communs if adaptation[k] >= mediane_adapt]
    faible = [k for k in communs if adaptation[k] < mediane_adapt]

    def correl(groupe):
        x = [exposition[k] for k in groupe]
        y = [cout_dette[k] for k in groupe]
        return stats.pearsonr(x, y)

    r_all, p_all = correl(communs)
    r_forte, p_forte = correl(forte)
    r_faible, p_faible = correl(faible)

    print(f"\nCorrelation exposition / cout de la dette, ensemble du panel (n={len(communs)}) : r={r_all:.2f} (p={p_all:.3f})")
    print(f"  Pays a forte capacite d'adaptation (n={len(forte)}) : r={r_forte:.2f} (p={p_forte:.3f}) -> {[COUNTRIES[k] for k in forte]}")
    print(f"  Pays a faible capacite d'adaptation (n={len(faible)}) : r={r_faible:.2f} (p={p_faible:.3f}) -> {[COUNTRIES[k] for k in faible]}")
