from __future__ import annotations
from datetime import datetime, timedelta
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


@dataclass(frozen=True)
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
        self, other: Noeud, max_machine_gap=2, max_time_gap=timedelta(days=21)
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
