from abc import abstractmethod, ABC
from Noeud import Noeud
import numpy as np
import time, datetime

class AlgorithmeColoriage(ABC):
    """
    Classe abstraite d'algorithme de coloriage
    """

    @abstractmethod
    def trouver_coloriage(
        self, partition: dict[str, set[Noeud]]
    ) -> dict[int, list[str]]:
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

class DSATUR(AlgorithmeColoriage):
    """
    Algorithme de DSATUR
    """
    def trouver_coloriage(
            self, 
            partition: dict[str, set[Noeud]],
            voisins: dict[Noeud, set[Noeud]]
            ) -> dict[int, set[str]]:
        """
        :param partition: dico avec en clé la valeur du critere et la liste des noeuds ayant ce critere en valeurs
        :param voisins: dico avec chaque noeud en clé et l'ensemble des voisins du noeud en valeur
        :return: renvoie un dico avec la couleur en clé et l'ensemble des criteres à colorier avec cette couleur.
        """
        start = time.time()
        coloriage = {}
        dsat = {noeud: 0 for noeud in voisins.keys()}
        non_colorie = set(voisins.keys())
        degre = {noeud: len(voisins[noeud]) for noeud in voisins.keys()}
        
        # Précalcul des voisins par critère
        voisins_partition = {}
        for critere, noeuds in partition.items():
            voisins_critere = set()
            for noeud in noeuds:
                voisins_critere.update(voisins[noeud])
            voisins_partition[critere] = voisins_critere

        # Dictionnaire pour retrouver le critère d'un nœud
        noeud_to_critere = {}
        for critere, noeuds in partition.items():
            for noeud in noeuds:
                noeud_to_critere[noeud] = critere

        # Couleurs interdites par critère
        couleurs_interdites = {critere: set() for critere in partition.keys()}

        while non_colorie:
            # Sélection du nœud avec DSAT max (degré max en cas d'égalité)
            noeud_choisi = max(non_colorie, 
                              key=lambda n: (dsat[n], degre[n]))
            critere_choisi = noeud_to_critere[noeud_choisi]

            # Trouver la plus petite couleur disponible pour le critère
            couleur = 1
            while True:
                if couleur not in couleurs_interdites[critere_choisi]:
                    break
                couleur += 1

            # Ajouter le critère à la couleur
            if couleur not in coloriage:
                coloriage[couleur] = set()
            coloriage[couleur].add(critere_choisi)

            # Mettre à jour les couleurs interdites pour les critères voisins
            for voisin in voisins_partition[critere_choisi]:
                critere_voisin = noeud_to_critere[voisin]
                couleurs_interdites[critere_voisin].add(couleur)

            # Mettre à jour les DSAT pour les nœuds voisins non coloriés
            for voisin in voisins[noeud_choisi]:
                if voisin in non_colorie:
                    critere_v = noeud_to_critere[voisin]
                    dsat[voisin] = len(couleurs_interdites[critere_v])

            # Retirer tous les nœuds du critère colorié
            non_colorie.difference_update(partition[critere_choisi])

        end = time.time()
        print(f"Temps d'exécution DSATUR: {end - start:.4f} secondes")
        return coloriage
    
if __name__=="__main__":
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
        liste_noeuds,
        critere="codeof"
    )
    voisins = Noeud.voisins_noeud(liste_noeuds, max_machine_gap=4, max_time_gap=timedelta(days=5))

    # Test de DSATUR
    algo = DSATUR()
    coloriage = algo.trouver_coloriage(partition=partition, voisins=voisins)
    print(coloriage)