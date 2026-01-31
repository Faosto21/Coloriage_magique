"""
Fichier contenant notre 2e algorithme testé qui n'était pas concluant car trouvait 91 couleurs alors que
DSATUR arrivait à en trouver presque moitié moins pour colorier le graphe
"""

from operators.AlgorithmeColoriage import AlgorithmeColoriage
from core.Noeud import Noeud
from datetime import datetime
from typing import List


# Fonction pour calculer le degre des voisins
def degre(noeud: Noeud, voisins: dict[Noeud, set[Noeud]]):
    return len(voisins[noeud])


class WelshPowell(AlgorithmeColoriage):
    """
    Classe héritée de la classe abstraite "AlgorithmeColoriage" et qui utilise l'algorithme de Welsh-Powell pour
    trouver le coloriage d'un graphe.
    """

    def trouver_coloriage(
        self, 
        liste_noeuds: List[Noeud], 
        critere: str
        ) -> dict[int, set[str]]:
        """
        A partir de la liste des noeuds et d'fun critère, associe une couleur à chaque partie de la partition.\n
        Par exemple, le résultat est sous la forme : \n
        {(201.1, 203, 205):[valeur1_du_critere,valeur3_du_critere], \n
        (50.20, 209, 199):[valeur2_du_critere,valeur4_du_critere]} \n
        Cela signifie que les parties ayant valeur1_du_critere et valeur3_du_critere seront coloriés avec la couleur RGB (201.1, 203, 205)\n
        Et les partie ayant valeur2_du_critere et valeur4_du_critere seront coloriés avec la couleur (50.20, 209, 199)


        :param liste_noeuds: Dictionnaire dont les clés sont les différentes valeurs du critère et la valeurs l'ensemble des noeuds ayant cette valeur de critère
        :type liste_noeuds: List[Noeud]
        :param critere: String correspondant au critere que l'on souhaite différencier sur notre coloriage
        :type critere: str
        :return: Dictionnaire dont les clés sont le numéro de couleur et la valeur la liste des valeurs de critères qui seront coloriés de cette couleur
        :rtype: dict[int, set[str]]
        """
        partition = Noeud.partition(liste_noeuds, critere=critere)  # Partition de la liste de noeud selon le critère par défaut codeof
        voisins = Noeud.voisins_noeud(liste_noeuds)  # Dictionnaire des voisins des noeuds
        voisins_partition = {
            critere: set.union(
                *[voisins[noeud] for noeud in noeuds]
            )  # Dictionnaires des voisins de chaque partie de partition
            for critere, noeuds in partition.items()
        }

        critere = {}
        for valeur, noeuds in partition.items():
            for noeud in noeuds:
                critere[noeud] = valeur
        # Initialisation du dictionnaire associant les couleurs aux noeuds
        couleurs_noeuds = {}
        couleur_actuelle = 1
        meme_couleur = []

        # On trie les sommets de la liste par ordre decroissant
        liste_noeuds.sort(key=lambda noeud: degre(noeud, voisins), reverse=True)

        # Tant qu'il reste des sommets non encore colores
        while len(couleurs_noeuds) < len(liste_noeuds):

            # On attribue un couleur au premier non colore par ordre de degre decroissant
            for noeud in liste_noeuds:
                if noeud not in couleurs_noeuds:
                    premier = critere[noeud]
                    break  # on trouve le premier et on sort de la boucle

            ensemble_voisins = (
                set.union(*[voisins_partition[critere] for critere in meme_couleur])
                if meme_couleur
                else set()
            )
            # if premier not in (set.union(*[voisins_partition[critere] for critere in meme_couleur])):

            if noeud not in ensemble_voisins:
                meme_couleur.append(premier)

            else:
                couleur_actuelle += 1
                meme_couleur = [premier]

            for noeud in partition[premier]:
                couleurs_noeuds[noeud] = couleur_actuelle

        # On construit maintenant le dictionnaire resultat
        res = {}

        for critere, noeuds in partition.items():
            # on suppose que tous les noeuds de la partie ont la même couleur
            noeud_exemple = next(
                iter(noeuds)
            )  # pour recuperer un noeud dans l'ensemble des noeuds associes a la valeur de critere
            if noeud_exemple in couleurs_noeuds:
                c = couleurs_noeuds[noeud_exemple]
            else:
                c = couleurs_noeuds[critere]

            if c not in res:
                res[c] = set()

            res[c].add(critere)

        return res


if __name__ == "__main__":
    from datetime import datetime, timedelta
    import pandas as pd
    from core.Noeud import Noeud

    data = pd.read_csv("ressources/Planification.txt", dtype=str, sep=";")
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
        liste_noeuds,
        critere="codof"
    )
    voisins = Noeud.voisins_noeud(liste_noeuds, max_machine_gap=4, max_time_gap=timedelta(days=5))

    # Test de DSATUR
    wp = WelshPowell()
    coloriage = wp.trouver_coloriage(liste_noeuds=liste_noeuds, critere="codof")
    print(f"Le coloriage est : {coloriage}")