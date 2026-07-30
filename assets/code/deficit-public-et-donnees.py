"""Solde nominal des administrations publiques (% du PIB) - notifications Eurostat.

Script utilise pour la note "Deficit public et donnees : ce que mesurent
(vraiment) les chiffres" (cameron-silva.fr/blog/deficit-public-et-donnees.html).
"""

import pandas as pd
import eurostat

# Code de dataset Eurostat : notification de la procedure de deficit excessif
df = eurostat.get_data_df("gov_10dd_edpt1")

# B9 = capacite (+) ou besoin (-) de financement des administrations publiques
solde = df[df["na_item"] == "B9"].melt(
    id_vars=["geo\\TIME_PERIOD"], var_name="annee", value_name="pct_pib"
)
solde = solde.rename(columns={"geo\\TIME_PERIOD": "pays"})
solde["annee"] = solde["annee"].astype(int)

fr = solde[solde["pays"] == "FR"].sort_values("annee")
print(fr.tail(10))
