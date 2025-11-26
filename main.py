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


def voisins_noeud(
    liste_noeuds: list[Noeud],
    max_machine_gap: int = 2,
    max_time_gap: timedelta = timedelta(days=21),
) -> dict[Noeud, set[Noeud]]:
    """
    Renvoie le dictionnaire des voisins de chaque noeud.

    :param liste_noeuds: Liste de tous les noeuds dont il faut trouver les voisins.
    :type liste_noeuds: list[Noeud]
    :param max_machine_gap: Ecart maximale en terme d'indice dans la liste de machines pour être considéré voisin.
    :type max_machine_gap: int
    :param max_time_gap: Ecart maximale en terme de temps pour être considéré voisin.
    :type max_time_gap: timedelta
    :return: Dictionnaire avec pour clé un noeud et pour valeur l'ensemble de ses voisins
    :rtype: dict[Noeud, set[Noeud]]
    """
    voisins = {noeud: set() for noeud in liste_noeuds}
    n = len(liste_noeuds)
    for i in range(n - 1):
        noeud1 = liste_noeuds[i]
        for j in range(i + 1, n):
            noeud2 = liste_noeuds[j]
            if noeud1.est_voisin(noeud2, max_machine_gap, max_time_gap):
                voisins[noeud1].add(noeud2)
                voisins[noeud2].add(noeud1)
    return voisins


print(len(voisins_noeud(liste_noeuds)[liste_noeuds[0]]))
