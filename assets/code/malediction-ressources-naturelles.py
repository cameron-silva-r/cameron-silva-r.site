"""La malediction des ressources naturelles, testee avec des donnees reelles :
les pays riches en petrole/mineraux ont-ils une croissance plus instable et
une gouvernance plus faible que les autres ?

Script utilise pour la note "La malediction des ressources naturelles existe-t-elle
vraiment ?" (cameron-silva.fr/blog/malediction-ressources-naturelles.html).

Source : Banque mondiale, World Development Indicators (API REST, sans cle).
"""

import statistics
import requests

COUNTRIES = {
    "NGA": "Nigeria", "AGO": "Angola", "SAU": "Arabie saoudite",
    "ARE": "Émirats arabes unis", "NOR": "Norvège", "QAT": "Qatar",
    "KWT": "Koweït", "RUS": "Russie", "DZA": "Algérie", "IRQ": "Irak",
    "KAZ": "Kazakhstan", "CHL": "Chili", "BWA": "Botswana",
    "COD": "RD Congo", "AUS": "Australie", "CAN": "Canada", "TCD": "Tchad",
}

INDICATORS = {
    "NY.GDP.TOTL.RT.ZS": "rentes_ressources_pib",   # % PIB, total (petrole+gaz+minerais+bois+charbon)
    "NY.GDP.PETR.RT.ZS": "rentes_petrole_pib",       # % PIB, petrole seul
    "GOV_WGI_CC.EST": "controle_corruption",         # indice WGI, -2.5 a +2.5
    "GOV_WGI_GE.EST": "efficacite_gouvernementale",  # indice WGI, -2.5 a +2.5
}


def fetch_indicator(code, iso3_codes, mrv=6):
    """Derniere valeur non nulle par pays (les mrv les plus recents peuvent
    etre nuls pour certains pays selon l'indicateur)."""
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
            out[iso3] = row["value"]
    return out


def fetch_growth_volatility(iso3_codes, years=15):
    """Ecart-type de la croissance du PIB reel sur les `years` dernieres
    annees disponibles, par pays (mesure de l'instabilite de la croissance)."""
    url = (
        f"https://api.worldbank.org/v2/country/{';'.join(iso3_codes)}"
        f"/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=1000&mrv={years}"
    )
    data = requests.get(url, timeout=20).json()
    by_country = {}
    for row in data[1]:
        if row["value"] is not None:
            by_country.setdefault(row["countryiso3code"], []).append(row["value"])
    return {
        iso3: round(statistics.stdev(values), 2)
        for iso3, values in by_country.items() if len(values) >= 5
    }


def build_dataset():
    iso3_codes = list(COUNTRIES.keys())
    series = {name: fetch_indicator(code, iso3_codes) for code, name in INDICATORS.items()}
    volatilite = fetch_growth_volatility(iso3_codes)

    dataset = {}
    for iso3, nom in COUNTRIES.items():
        dataset[iso3] = {"pays": nom, "volatilite_croissance": volatilite.get(iso3)}
        for name in INDICATORS.values():
            dataset[iso3][name] = series[name].get(iso3)
    return dataset


if __name__ == "__main__":
    from scipy import stats

    dataset = build_dataset()
    rows = sorted(
        dataset.items(),
        key=lambda kv: kv[1]["rentes_ressources_pib"] or 0,
        reverse=True,
    )

    print("Pays classes par rentes des ressources naturelles (% du PIB) :")
    for iso3, d in rows:
        print(
            f"  {d['pays']:<22} rentes={d['rentes_ressources_pib']:>6.1f}  "
            f"petrole={d['rentes_petrole_pib']:>6.1f}  "
            f"volatilite_croiss={d['volatilite_croissance']:>5.2f}  "
            f"controle_corruption={d['controle_corruption']:>5.2f}  "
            f"efficacite_gouv={d['efficacite_gouvernementale']:>5.2f}"
        )

    rentes = [d["rentes_ressources_pib"] for _, d in rows]
    volat = [d["volatilite_croissance"] for _, d in rows]
    corruption = [d["controle_corruption"] for _, d in rows]
    efficacite = [d["efficacite_gouvernementale"] for _, d in rows]

    r1, p1 = stats.pearsonr(rentes, volat)
    r2, p2 = stats.pearsonr(rentes, corruption)
    r3, p3 = stats.pearsonr(rentes, efficacite)

    print(f"\nCorrelation rentes ressources / volatilite de la croissance : r={r1:.2f} (p={p1:.3f})")
    print(f"Correlation rentes ressources / controle de la corruption   : r={r2:.2f} (p={p2:.3f})")
    print(f"Correlation rentes ressources / efficacite gouvernementale  : r={r3:.2f} (p={p3:.3f})")
