from abc import abstractmethod, ABC
from typing import List
from core.Noeud import Noeud
import numpy as np
from datetime import timedelta


class AlgorithmeColoriage(ABC):
    """
    Classe abstraite d'algorithme de coloriage
    """

    @abstractmethod
    def trouver_coloriage(
        self,
        liste_noeuds: List[Noeud],
        max_machine_gap: int,
        max_time_gap: timedelta,
        critere: str,
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


def ecritureFichierColoriage(
    coloriage: dict[tuple[float, float, float], set[str]],
    chemin_donnees: str,
    choix_critere: str,
):
    """
    :param coloriage: un dico avec la couleur en clé et la liste des criteres à colorier avec cette couleur.
    :param choix_critere: une string correspondant au critère selectionné
    :param chemin_donnees: une string correspondant au chemin du jeu de données utilisé
    :return: None. Créer une copie du fichier d'entrée et ajoute une colonne donnant la couleur associée à chaque case
    du tableau.
    """

    couleur_par_critere = {}
    # On inverse le sens du dictionnaire coloriage dans couleur_par_critere
    for couleur, criteres in coloriage.items():
        for c in criteres:
            couleur_par_critere[c] = couleur

    # Lecture et ecriture du fichier

    with open(chemin_donnees, "r", encoding="utf-8") as f_in, open(
        "ressources/Resultats_planification.txt", "w", encoding="utf-8"
    ) as f_out:

        # Header du fichier
        header = f_in.readline().rstrip("\n")
        colonnes = header.split(";")

        index = colonnes.index(choix_critere)

        f_out.write(header + ";couleur\n")

        # Lignes de donnees
        for line in f_in:
            line = line.rstrip("\n")
            if line == "":
                continue

            cols = line.split(";")

            # colonne critrere = index
            critere = cols[index] if len(cols) > index else ""
            couleur = list(map(float,couleur_par_critere.get(str(critere), ""))) # vide si pas trouve

            f_out.write(line + ";" + str(couleur) + "\n")


if __name__ == "__main__":
    from datetime import datetime
    import pandas as pd

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

    # Test de DSATUR
    algo_dsat = DSATUR()
    coloriage = algo_dsat.trouver_coloriage(liste_noeuds=liste_noeuds, critere="codof")
    print(f"Le coloriage est : {coloriage}")
    ecritureFichierColoriage(coloriage, "ressources/Planification.txt", "codof")
