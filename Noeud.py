from __future__ import annotations
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass


def overlap(debut1: datetime, debut2: datetime, fin1: datetime, fin2: datetime) -> bool:
    """
    Vérifie si les deux périodes (debut1,fin1) et (debut2,fin2) se chevauchent.

    :param debut1: Début de la première période.
    :type debut1: datetime
    :param debut2: Début de la deuxième période.
    :type debut2: datetime
    :param fin1: Fin de la première période.
    :type fin1: datetime
    :param fin2: Fin de la deuxième période.
    :type fin2: datetime
    :return: True si les deux périodes se chevauchent et False sinon.
    :rtype: bool
    """
    return (fin1 > debut2 and debut1 < fin2) or (fin2 > debut1 and debut2 < fin1)


@dataclass(frozen=True)  # Pour rendre immutable et être utilisé en clé
class Noeud:
    """
    Classe représentant une opération de production avec comme attribut toutes les colonnes de Planification.
    L'un de ses attributs sera ensuite le critère pour effectuer le coloriage.
    """

    id_noeud: int
    indice_machine: int
    centre: str
    codeprod: str
    codeof: str
    sequence: str
    codeop: str
    date_debut: datetime
    date_fin: datetime

    def est_voisin(
        self, other: Noeud, max_machine_gap=3, max_time_gap=timedelta(days=21)
    ) -> bool:
        """
        Vérifie si deux noeuds sont voisins l'un de l'autre

        :param self: 1er sommet
        :param other: 2ème sommet dont on veut vérifier s'il est voisin avec self.
        :param max_machine_gap: Ecart maximale en terme d'indice dans la liste de machines pour être considéré voisin.
        :param max_time_gap: Ecart maximale en terme de temps pour être considéré voisin.
        :return: True si ils sont voisins et False sinon
        :rtype: bool
        """
        if abs(self.indice_machine - other.indice_machine) > max_machine_gap:
            return False
        if overlap(self.date_debut, other.date_debut, self.date_fin, other.date_fin):
            return True
        else:
            min_fin = min(self.date_fin, other.date_fin)
            max_debut = max(self.date_debut, other.date_fin)
            return max_debut - min_fin <= max_time_gap

    @staticmethod
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
        voisins: dict[Noeud, set[Noeud]] = {noeud: set() for noeud in liste_noeuds}
        n = len(liste_noeuds)
        for i in range(n - 1):
            noeud1 = liste_noeuds[i]
            for j in range(i + 1, n):
                noeud2 = liste_noeuds[j]
                if noeud1.est_voisin(noeud2, max_machine_gap, max_time_gap):
                    voisins[noeud1].add(noeud2)
                    voisins[noeud2].add(noeud1)
        return voisins

    @staticmethod
    def partition(
        liste_noeuds: list[Noeud], critere: str = "codeof"
    ) -> dict[any, set[Noeud]]:
        """
        Renvoie la partition de la liste des noeuds en fonction d'un critère choisi

        :param liste_noeuds: Liste des Noeuds dont on veut faire la partition.
        :type liste_noeuds: list[Noeud]
        :param critere: Critère pour la partition, c'est un des attributs des Noeuds.
        :type critere: str
        :return: Dictionnaire avec pour clé les valeurs du critère et en valeur l'ensemble des noeuds ayant cette valeur de critère.
        :rtype: dict[Any, set[Noeud]]
        """
        partition = defaultdict(set)
        for noeud in liste_noeuds:
            valeur_critere = noeud.__getattribute__(critere)
            partition[valeur_critere].add(noeud)
        return partition