"""Score de risque pays multi-composantes (methodologie inspiree de l'ICRG).

Script utilise pour la note "Evaluer le risque pays : cadre d'analyse et
limites des methodologies de notation" (cameron-silva.fr/blog/risque-pays-cadre-analyse.html).

Sources (API publique, sans cle) :
- Political : Worldwide Governance Indicators, Banque mondiale (6 dimensions)
- Economique : World Development Indicators, Banque mondiale (croissance, inflation, chomage, PIB/hab.)
- Financier : World Development Indicators, Banque mondiale (compte courant, reserves, dette publique)

Ponderation : Politique 50 % / Financier 25 % / Economique 25 % (structure ICRG : 100/50/50 points sur 200).
"""

import requests
import pandas as pd

COUNTRIES = {
    "FRA": "France", "DEU": "Allemagne", "ESP": "Espagne", "ITA": "Italie",
    "POL": "Pologne", "ROU": "Roumanie", "GBR": "Royaume-Uni",
    "MAR": "Maroc", "EGY": "Egypte", "NGA": "Nigeria", "ZAF": "Afrique du Sud",
    "TUR": "Turquie", "SAU": "Arabie saoudite", "ARE": "Emirats arabes unis",
    "CHN": "Chine", "IND": "Inde", "JPN": "Japon", "IDN": "Indonesie",
    "USA": "Etats-Unis", "BRA": "Bresil", "MEX": "Mexique", "CAN": "Canada",
}

# Political risk (Worldwide Governance Indicators, echelle -2.5 a +2.5)
WGI = {
    "GOV_WGI_VA.EST": "voice_accountability",
    "GOV_WGI_PV.EST": "political_stability",
    "GOV_WGI_GE.EST": "government_effectiveness",
    "GOV_WGI_RQ.EST": "regulatory_quality",
    "GOV_WGI_RL.EST": "rule_of_law",
    "GOV_WGI_CC.EST": "control_corruption",
}

# Economic risk
ECON = {
    "NY.GDP.MKTP.KD.ZG": "gdp_growth",
    "FP.CPI.TOTL.ZG": "inflation",
    "SL.UEM.TOTL.ZS": "unemployment",
    "NY.GDP.PCAP.CD": "gdp_per_capita",
}

# Financial risk
FIN = {
    "BN.CAB.XOKA.GD.ZS": "current_account_gdp",
    "FI.RES.TOTL.MO": "reserves_months_imports",
    "GC.DOD.TOTL.GD.ZS": "gov_debt_gdp",
}

ALL_INDICATORS = {**WGI, **ECON, **FIN}


def fetch_indicator(code, iso3_codes):
    """Recupere la derniere valeur non nulle disponible pour un indicateur, pour une liste de pays.

    mrv=5 renvoie les 5 dernieres periodes (certaines peuvent etre nulles,
    l'API renvoyant parfois une annee recente sans donnee reelle) ; on
    conserve, pour chaque pays, la valeur non nulle la plus recente.
    """
    url = (
        f"https://api.worldbank.org/v2/country/{';'.join(iso3_codes)}"
        f"/indicator/{code}?format=json&per_page=1000&mrv=5"
    )
    resp = requests.get(url, timeout=20)
    payload = resp.json()
    if len(payload) < 2 or payload[1] is None:
        return {}
    values = {}
    for row in sorted(payload[1], key=lambda r: r["date"], reverse=True):
        iso = row["countryiso3code"]
        if row["value"] is not None and iso not in values:
            values[iso] = row["value"]
    return values


def build_dataset():
    iso3_codes = list(COUNTRIES.keys())
    data = {"pays": [COUNTRIES[c] for c in iso3_codes]}
    for code, name in ALL_INDICATORS.items():
        values = fetch_indicator(code, iso3_codes)
        data[name] = [values.get(c) for c in iso3_codes]
    return pd.DataFrame(data, index=iso3_codes)


def minmax(series, higher_is_better=True):
    normalized = (series - series.min()) / (series.max() - series.min()) * 100
    return normalized if higher_is_better else 100 - normalized


def score(df):
    # Composante politique : moyenne des 6 dimensions WGI, ramenees de [-2.5, 2.5] a [0, 100]
    wgi_cols = list(WGI.values())
    political = df[wgi_cols].apply(lambda s: (s + 2.5) / 5 * 100).mean(axis=1)

    # Composante economique : croissance et PIB/habitant "plus haut = mieux",
    # inflation et chomage "plus bas = mieux"
    economic = pd.concat(
        [
            minmax(df["gdp_growth"], True),
            minmax(df["inflation"], False),
            minmax(df["unemployment"], False),
            minmax(df["gdp_per_capita"], True),
        ],
        axis=1,
    ).mean(axis=1)

    # Composante financiere : compte courant et reserves "plus haut = mieux",
    # dette publique "plus bas = mieux"
    financial = pd.concat(
        [
            minmax(df["current_account_gdp"], True),
            minmax(df["reserves_months_imports"], True),
            minmax(df["gov_debt_gdp"], False),
        ],
        axis=1,
    ).mean(axis=1)

    df["score_politique"] = political.round(1)
    df["score_economique"] = economic.round(1)
    df["score_financier"] = financial.round(1)
    df["score_compose"] = (
        0.5 * political + 0.25 * financial + 0.25 * economic
    ).round(1)
    return df.sort_values("score_compose", ascending=False)


if __name__ == "__main__":
    dataset = build_dataset()
    resultat = score(dataset)
    print(
        resultat[
            ["pays", "score_politique", "score_economique", "score_financier", "score_compose"]
        ].to_string(index=False)
    )
