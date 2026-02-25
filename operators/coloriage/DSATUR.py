from typing import List
from datetime import timedelta
import numpy as np

from operators.coloriage.AlgorithmeColoriage import AlgorithmeColoriage
from core.Noeud import Noeud
from operators.coloriage.GenerateurCouleur import generateur_couleur


class DSATUR(AlgorithmeColoriage):
    """
    Algorithme de DSATUR
    """

    def trouver_coloriage(
        self,
        liste_noeuds: List[Noeud],
        max_machine_gap: int = 7,
        max_time_gap: timedelta = timedelta(days=7),
        critere: str = "codof",
    ) -> dict[tuple[float, float, float], set[str]]:

        # Initialisation
        partition = Noeud.partition(
            liste_noeuds, critere=critere
        )  # Partition de la liste de noeud selon le critère par défaut codeof
        voisins = Noeud.voisins_noeud(
            liste_noeuds, max_machine_gap=max_machine_gap, max_time_gap=max_time_gap
        )  # Dictionnaire des voisins des noeuds
        coloriage = (
            {}
        )  # objet qui sera retourné à la fin, il donnera pour chaque couleur ses criteres
        dsat = {
            noeud: 0 for noeud in voisins.keys()
        }  # permet de suivre le score dsat de chaque noeud
        non_colorie = set(voisins.keys())  # pour avoir un suivi des noeuds non coloriés
        degre = {noeud: len(voisins[noeud]) for noeud in voisins.keys()}

        # Dico des voisins par critère (équivalent à la méthode de thomas mais en plus simple à comprendre)
        # voisins_partition associe à chaque critère l'ensemble des voisins des noeuds ayant ce critere
        # ca nous permettra de connaitre les voisins du critere du noeud choisi
        voisins_partition = {}
        for critere, noeuds in partition.items():
            voisins_critere = set()
            for noeud in noeuds:
                voisins_critere.update(voisins[noeud])
            voisins_partition[critere] = voisins_critere

        # Dico pour retrouver le critere du noeud choisi
        critere_du_noeud = {}
        for critere, noeuds in partition.items():
            for noeud in noeuds:
                critere_du_noeud[noeud] = critere

        # Couleurs adjacentes par critere, permettra de mettre à jour le dsat des voisins du critere colorié
        # Si un critere a une couleur adjacente alors il n'a pas le droit de l'avoir
        couleurs_adjacentes = {critere: set() for critere in partition.keys()}

        while non_colorie:
            # Sélection du nœud avec DSAT max (degré max en cas d'égalité)
            noeud_choisi = max(non_colorie, key=lambda n: (dsat[n], degre[n]))

            # On trouve le critère choisi du noeud sélectionné
            critere_choisi = critere_du_noeud[noeud_choisi]

            # On cherche les couleurs possibles pour le critère en évitant les couleurs adjacentes
            # car 2 criteres adjacent ne peuvent avoir la meme couleur
            couleurs_possibles = set(coloriage.keys())
            couleurs_possibles.difference_update(couleurs_adjacentes[critere_choisi])

            # On choisit une couleur aléatoire pour le critere parmi les possibles
            if couleurs_possibles:
                couleur = np.random.choice(
                    list(couleurs_possibles)
                )  # Conversion en liste pour random
            # Sinon on prend la couleur suivante du coloriage
            else:
                couleur = len(coloriage)

            # On ajoute la couleur au coloriage si elle n'y est pas et on y associe le critère
            if couleur not in coloriage:
                coloriage[couleur] = set()
            coloriage[couleur].add(critere_choisi)

            # On met à jour les DSAT uniquement pour les voisins affectés
            # Autrement dit si la couleur est nouvelle pour le voisin
            for voisin_du_critere in voisins_partition[critere_choisi]:
                if voisin_du_critere in non_colorie:
                    # On retrouve le critere du voisin
                    critere_du_voisin = critere_du_noeud[voisin_du_critere]

                    # On ajoute la couleur aux couleurs_adjacentes du critere_du_voisin
                    couleurs_adjacentes[critere_du_voisin].add(couleur)

                    # On met à jour le dsat du voisin du critère
                    dsat[voisin_du_critere] = len(
                        couleurs_adjacentes[critere_du_voisin]
                    )

            # On retire tous les noeuds de ce critère de non_colorie
            non_colorie.difference_update(partition[critere_choisi])

        # On va maintenant attribuer les couleurs générées à chaque clé de notre coloriage
        liste_couleurs = generateur_couleur(len(coloriage))
        dico_couleurs = dict(enumerate(liste_couleurs))

        # On transforme les np.array en tuple pour qu'ils soient hashables et les mettre en clé
        dico_couleurs_tuple = {key: tuple(arr) for key, arr in dico_couleurs.items()}

        # On obtient le dictionnaire avec clé = couleur RGB et valeur = ensemble des noeuds de cette couleur
        coloriage_final = {
            couleur_rgb: coloriage[numero]
            for numero, couleur_rgb in dico_couleurs_tuple.items()
        }

        return coloriage_final
