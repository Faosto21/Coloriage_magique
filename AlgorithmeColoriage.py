from abc import abstractmethod, ABC
from Noeud import Noeud
import numpy as np

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
            voisins : dict[Noeud, set[Noeud]]
            ) -> dict[int, set[str]]:
        """
        :param partition: dico avec en clé la valeur du critere et la liste des noeuds ayant ce critere en valeurs
        :param voisins: dico avec chaque noeud en clé et l'ensemble des voisins du noeud en valuer
        :return: renvoie un dico avec la couleur en clé et la liste des criteres à colorier avec cette couleur.
        """
        # Initialisation
        coloriage = {}
        dsat = {noeud : 0 for noeud in voisins.keys()}
        non_colorie = set(voisins.keys())
        # voisins_partition associe à chaque critère l'ensemble des voisins des noeuds ayant ce critere
        # ca nous permettra de connaitre les voisins du critere du noeud choisi
        voisins_partition = {
            critere: set.union(
                *[voisins[noeud] for noeud in noeuds], set()
            )
            for critere, noeuds in partition.items()
        }

        while non_colorie:
            # On choisit le noeud avec le DSAT maximum et degré max en cas d'égalité
            max_dsat = -1
            noeud_choisi = None
            for node in non_colorie:
                if (dsat[node] > max_dsat 
                or (dsat[node] == max_dsat 
                    and len(voisins[node]) > len(voisins[noeud_choisi or node]))
                ):
                    max_dsat = dsat[node]
                    noeud_choisi = node
            
            # On trouve le critere du noeud choisi
            critere_choisi = next(critere for critere, noeuds in partition.items() if noeud_choisi in noeuds)
            
            # On trouve la plus petite couleur disponible
            couleur = None
            for color in sorted(coloriage.keys()):
                conflit = False
                # On vérifie si critere_choisi peut avoir cette couleur, cad si la couleur est utilisée par un voisin
                # dans voisins_partitions[critere_choisi], car on peut avoir une meme couleur pour 2 criteres différents
                # si leurs partitions respectives sont "éloignées"
                for voisin in voisins_partition[critere_choisi]:
                    voisin_critere = next((crit for crit, set_noeuds in partition.items() if voisin in set_noeuds), None)
                    if voisin_critere in coloriage[color]:
                        conflit = True
                        break
                if not conflit:
                    couleur = color
                    break
            
            # Si on trouve pas de couleurs possible on en créé une nouvelle
            if couleur is None:
                couleur = max(coloriage.keys()) + 1 if coloriage else 1
                coloriage[couleur] = set()
            
            # On ajoute le critère à cette couleur (et donc la partition associée au final)
            coloriage[couleur].add(critere_choisi)
            
            # On retire tous les noeuds de ce critère de non_colorie (car ils sont mtn coloriés lol)
            non_colorie.difference_update(partition[critere_choisi])
            
            # On met à jour les DSAT des noeuds étant dans non coloriés
            for voisin in voisins_partition[critere_choisi]:
                if voisin in non_colorie:
                    dsat[voisin] += 1
        
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