from operators.AlgorithmeColoriage import AlgorithmeColoriage
from core.Noeud import Noeud
from datetime import datetime


# Fonction pour calculer le degre des voisins
def degre(noeud: Noeud, voisins: dict[Noeud, set[Noeud]]):
    return len(voisins[noeud])


class WelshPowell(AlgorithmeColoriage):
    """
    Classe héritée de la classe abstraite "AlgorithmeColoriage" et qui utilise l'algorithme de Welsh-Powell pour
    trouver le coloriage d'un graphe.
    """

    def trouver_coloriage(
        self, partition: dict[str, set[Noeud]], voisins: dict[Noeud, set[Noeud]]
    ) -> dict[int, set[str]]:
        """
        A partir d'une partition des noeuds selon un critère, associe une couleur à chaque partie de la partition.\n
        Par exemple, le résultat est sous la forme : \n
        {1:[valeur1_du_critere,valeur3_du_critere], \n
        2:[valeur2_du_critere,valeur4_du_critere]} \n
        Cela signifie que les parties ayant valeur1_du_critere et valeur3_du_critere seront coloriés avec la couleur 1 \n
        Et les partie ayant valeur2_du_critere et valeur4_du_critere seront coloriés avec la couleur 2


        :param partition: Dictionnaire dont les clés sont les différentes valeurs du critère et la valeurs l'ensemble des noeuds ayant cette valeur de critère
        :type partition: dict[str, set[Noeud]]
        :return: Dictionnaire dont les clés sont le numéro de couleur et la valeur la liste des valeurs de critères qui seront coloriés de cette couleur
        :rtype: dict[int, list[str]]
        """
        voisins_partition = {
            critere: set.union(
                *[voisins[noeud] for noeud in noeuds]
            )  # Dictionnaires des voisins de chaque partie de partition
            for critere, noeuds in partition.items()
        }

        # On recree la liste de tous les sommets
        liste_noeuds = []
        for val in partition:
            for noeud in partition[val]:
                liste_noeuds.append(noeud)

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
    wp = WelshPowell()
    Noeud1 = Noeud(
        1,
        1,
        "1",
        "1",
        "1",
        "1",
        "1",
        datetime(2025, 11, 27, 9, 0, 0),
        datetime(2025, 11, 27, 10, 0, 0),
    )
    Noeud2 = Noeud(
        2,
        2,
        "2",
        "2",
        "2",
        "2",
        "2",
        datetime(2025, 11, 28, 9, 0, 0),
        datetime(2025, 11, 28, 10, 0, 0),
    )
    Noeud3 = Noeud(
        3,
        3,
        "3",
        "3",
        "3",
        "3",
        "3",
        datetime(2025, 11, 29, 9, 0, 0),
        datetime(2025, 11, 29, 10, 0, 0),
    )
    Noeud4 = Noeud(
        4,
        4,
        "4",
        "4",
        "4",
        "4",
        "4",
        datetime(2025, 11, 30, 9, 0, 0),
        datetime(2025, 11, 30, 10, 0, 0),
    )

    partition = {
        "val_crit1": {Noeud1},
        "val_crit2": {Noeud2},
        "val_crit3": {Noeud3, Noeud4},
    }
    voisins = {
        Noeud1: {Noeud2, Noeud4},
        Noeud2: {Noeud1, Noeud3, Noeud4},
        Noeud3: {Noeud2},
        Noeud4: {Noeud1, Noeud2},
    }

    print(wp.trouver_coloriage(partition, voisins))
