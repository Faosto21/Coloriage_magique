from datetime import datetime, timedelta
import pandas as pd
from Noeud import Noeud


data = pd.read_csv("ressources/Planification.txt", sep=";")
machines = pd.read_csv("ressources/Machine.txt")
mapping_machines = {machines["centre"][i]: i for i in range(len(machines))}

liste_noeuds = [
    Noeud(
        i,
        mapping_machines[ope["centre"]],
        ope["centre"],
        ope["codprod"],
        ope["codof"],
        ope["sequence"],
        ope["codop"],
        datetime.fromisoformat(ope["dtedeb"]),
        datetime.fromisoformat(ope["dtefin"]),
    )
    for i, ope in data.iterrows()
]


partition = Noeud.partition(
    liste_noeuds
)  # Partition de la liste de noeud selon le critère par défaut codeof
voisins = Noeud.voisins_noeud(liste_noeuds)  # Dictionnaire des voisins des noeuds
voisins_partition = {
    critere: set.union(
        *[voisins[noeud] for noeud in noeuds]
    )  # Dictionnaires des voisins de chaque partie de partition
    for critere, noeuds in partition.items()
}
print(len(partition))  # 108 valeurs différentes de codeof

print(
    voisins_partition["OF00000001"]
)  # Union des voisins de l'ensemble des Noeuds ayant le codeof = OF00000001
