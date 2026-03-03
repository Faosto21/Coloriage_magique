from operators.coloriage.AlgorithmeColoriage import AlgorithmeColoriage
from core.Noeud import Noeud
from datetime import datetime, timedelta
from typing import List
from operators.coloriage.GenerateurCouleur import generateur_couleur


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
        max_machine_gap: int = 7,
        max_time_gap: timedelta = timedelta(days=7),
        critere: str = "codof",
    ) -> dict[tuple[float, float, float], set[str]]:
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
        :return: Dictionnaire dont les clés sont les couleurs RGB et la valeur la liste des valeurs de critères qui seront coloriés de cette couleur
        :rtype: dict[tuple[float, float,float], set[str]]
        """
        # Partition et calcul des voisins
        partition = Noeud.partition(liste_noeuds, critere=critere)
        voisins = Noeud.voisins_noeud(
            liste_noeuds, max_machine_gap=max_machine_gap, max_time_gap=max_time_gap
        )

        # Mapping noeud -> critere
        critere_du_noeud: dict[Noeud, str] = {}
        for valeur, noeuds in partition.items():
            for noeud in noeuds:
                critere_du_noeud[noeud] = valeur

        # Construction des voisins de chaque critere (union des voisins de tous les noeuds ayant ce critere)
        voisins_criteres: dict[str, set[str]] = {c: set() for c in partition.keys()}
        for c, noeuds in partition.items():
            for noeud in noeuds:
                for v in voisins.get(noeud, set()):
                    voisins_criteres[c].add(critere_du_noeud.get(v))
            # remove self if present
            voisins_criteres[c].discard(c)

        # Degré par crière
        degre_criteres = {c: len(neigh) for c, neigh in voisins_criteres.items()}

        # Tri des critères par ordre décroissant de degré
        criteres_ordonnes = sorted(
            partition.keys(), key=lambda c: degre_criteres[c], reverse=True
        )

        # Algorithme de Welsh-Powell : on parcourt les critères dans l'ordre décroissant de degré et on les colore avec la première couleur disponible
        coloriage_idx: dict[int, set[str]] = {}
        couleur_idx = 0
        non_colories = set(criteres_ordonnes)

        while non_colories:
            # On prend le premier critere non colorié dans l'ordre décroissant de degré
            for c in criteres_ordonnes:
                if c in non_colories:
                    current = c
                    break

            coloriage_idx[couleur_idx] = {current}
            non_colories.remove(current)

            # On essaye de colorier les autres critères non coloriés avec la même couleur si ils ne sont pas voisins du critere actuel
            for c in criteres_ordonnes:
                if c in non_colories:
                    if all(
                        (
                            c not in voisins_criteres[other]
                            and other not in voisins_criteres[c]
                        )
                        for other in coloriage_idx[couleur_idx]
                    ):
                        coloriage_idx[couleur_idx].add(c)
                        non_colories.remove(c)

            couleur_idx += 1

        # Mapping de l'index de couleur vers une couleur RGB générée aléatoirement
        liste_couleurs = generateur_couleur(len(coloriage_idx))
        dico_couleurs = dict(enumerate(liste_couleurs))
        dico_couleurs_tuple = {key: tuple(arr) for key, arr in dico_couleurs.items()}

        coloriage_final = {
            dico_couleurs_tuple[num]: criteres
            for num, criteres in coloriage_idx.items()
        }

        return coloriage_final
