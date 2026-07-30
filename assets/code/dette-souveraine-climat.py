"""Dette souveraine et climat : les pays les plus exposes empruntent-ils plus cher ?

Script utilise pour la note "Dette souveraine et climat : la vulnerabilite
climatique a-t-elle un prix ?" (cameron-silva.fr/blog/dette-souveraine-climat.html).

Sources (API publique Banque mondiale, sans cle) :
- Exposition climatique physique : World Development Indicators (WDI)
- Dette exterieure et service de la dette : International Debt Statistics (IDS)

Panel : 18 pays en developpement/emergents suivis par la Banque mondiale au
titre du systeme de notification de la dette exterieure (Debtor Reporting
System), couvrant des petits Etats insulaires, l'Asie du Sud/Sud-Est,
l'Afrique et l'Amerique latine.
"""

import requests
from scipy import stats

COUNTRIES = {
    "BGD": "Bangladesh", "VNM": "Vietnam", "PHL": "Philippines",
    "MOZ": "Mozambique", "MDV": "Maldives", "VUT": "Vanuatu", "FJI": "Fidji",
    "PAK": "Pakistan", "KEN": "Kenya", "NGA": "Nigeria", "ARG": "Argentine",
    "IDN": "Indonesie", "MAR": "Maroc", "ZAF": "Afrique du Sud",
    "EGY": "Egypte", "TUR": "Turquie", "IND": "Inde", "BRA": "Bresil",
}

INDICATORS = {
    "EN.POP.EL5M.ZS": "pop_zone_basse",       # population en zone <5m d'altitude
    "EN.CLC.MDAT.ZS": "exposition_historique",  # secheresses/inondations/temperatures extremes
    "EN.GHG.CO2.PC.CE.AR5": "co2_par_habitant",
    "DT.DOD.DECT.GN.ZS": "dette_externe_pib",   # dette exterieure, % RNB
    "DT.TDS.DECT.EX.ZS": "service_dette_export",  # service de la dette, % exportations
    "NY.GDP.PCAP.CD": "pib_par_habitant",
}


def fetch_indicator(code, iso3_codes):
    """Recupere la derniere valeur non nulle disponible pour un indicateur."""
    url = (
        f"https://api.worldbank.org/v2/country/{';'.join(iso3_codes)}"
        f"/indicator/{code}?format=json&per_page=1000&mrv=6"
    )
    data = requests.get(url, timeout=20).json()
    if len(data) < 2 or data[1] is None:
        return {}
    values = {}
    for row in sorted(data[1], key=lambda r: r["date"], reverse=True):
        iso = row["countryiso3code"]
        if row["value"] is not None and iso not in values:
            values[iso] = row["value"]
    return values


def build_dataset():
    iso3_codes = list(COUNTRIES.keys())
    series = {name: fetch_indicator(code, iso3_codes) for code, name in INDICATORS.items()}
    return {
        iso: {"pays": COUNTRIES[iso], **{name: series[name].get(iso) for name in series}}
        for iso in iso3_codes
    }


def minmax(values):
    lo, hi = min(values), max(values)
    return [(v - lo) / (hi - lo) * 100 for v in values]


def compute_exposure_index(dataset):
    isos = list(dataset.keys())
    zone_basse = minmax([dataset[i]["pop_zone_basse"] for i in isos])
    hist = minmax([dataset[i]["exposition_historique"] for i in isos])
    for i, iso in enumerate(isos):
        dataset[iso]["indice_exposition_climatique"] = round(
            (zone_basse[i] + hist[i]) / 2, 1
        )
    return dataset


if __name__ == "__main__":
    dataset = compute_exposure_index(build_dataset())
    ranked = sorted(
        dataset.items(), key=lambda kv: kv[1]["indice_exposition_climatique"], reverse=True
    )

    print("Pays classes par indice d'exposition climatique physique (0-100) :")
    for iso, d in ranked:
        print(
            f"  {d['pays']:<16} exposition={d['indice_exposition_climatique']:>5.1f}"
            f"  dette_ext_%RNB={d['dette_externe_pib']:>6.1f}"
            f"  service_dette_%export={d['service_dette_export']:>5.1f}"
            f"  co2/hab={d['co2_par_habitant']:.2f}"
        )

    exposition = [d["indice_exposition_climatique"] for _, d in ranked]
    dette = [d["dette_externe_pib"] for _, d in ranked]
    service = [d["service_dette_export"] for _, d in ranked]

    r_dette, p_dette = stats.pearsonr(exposition, dette)
    r_service, p_service = stats.pearsonr(exposition, service)
    print(f"\nCorrelation exposition climatique / dette exterieure (%RNB) : r={r_dette:.2f} (p={p_dette:.3f})")
    print(f"Correlation exposition climatique / service de la dette (%export) : r={r_service:.2f} (p={p_service:.3f})")
