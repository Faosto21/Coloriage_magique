from Noeud import Noeud
import numpy as np
import time
from AlgorithmeColoriage import AlgorithmeColoriage


class DSATUR2(AlgorithmeColoriage):
    """
    Algorithme de DSATUR
    """

    def trouver_coloriage(
        self, partition: dict[str, set[Noeud]], voisins: dict[Noeud, set[Noeud]]
    ) -> dict[int, set[str]]:
        """
        :param partition: dico avec en clé la valeur du critere et la liste des noeuds ayant ce critere en valeurs
        :param voisins: dico avec chaque noeud en clé et l'ensemble des voisins du noeud en valuer
        :return: renvoie un dico avec la couleur en clé et la liste des criteres à colorier avec cette couleur.
        """
        # Initialisation
        start = time.time()
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

            # On trouve la plus petite couleur disponible pour le critère en évitant les couleurs adjacentes
            # car 2 criteres adjacent ne peuvent avoir la meme couleur
            couleur = 1
            while True:
                if couleur not in couleurs_adjacentes[critere_choisi]:
                    break
                couleur += 1

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

                    # On ajoute la couleur aux couleurs_adjacentes du critere_du_voisin si elle n'y est pas
                    if couleur not in couleurs_adjacentes[critere_du_voisin]:
                        couleurs_adjacentes[critere_du_voisin].add(couleur)

                    # On met à jour le dsat du voisin du critère
                    dsat[voisin_du_critere] = len(
                        couleurs_adjacentes[critere_du_voisin]
                    )

            # On retire tous les noeuds de ce critère de non_colorie
            non_colorie.difference_update(partition[critere_choisi])

        end = time.time()
        print(end - start)
        return coloriage
