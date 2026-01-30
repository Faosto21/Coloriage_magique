from abc import abstractmethod, ABC
from typing import List
from core.Noeud import Noeud
import numpy as np
import time
from datetime import timedelta
from operators.test import generateur_couleur, evaluer
import basic_colormath

class AlgorithmeColoriage(ABC):
    """
    Classe abstraite d'algorithme de coloriage
    """

    @abstractmethod
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

class DSATUR(AlgorithmeColoriage):
    """
    Algorithme de DSATUR
    """
    def trouver_coloriage(
            self,
            liste_noeuds : List[Noeud],
            critere : str
            ) -> dict[int, set[str]]:
        """
        :param partition: dico avec en clé la valeur du critere et la liste des noeuds ayant ce critere en valeurs
        :param voisins: dico avec chaque noeud en clé et l'ensemble des voisins du noeud en valuer
        :return: renvoie un dico avec la couleur en clé et la liste des criteres à colorier avec cette couleur.
        """
        # Initialisation
        start = time.time()
        partition = Noeud.partition(liste_noeuds, critere=critere)  # Partition de la liste de noeud selon le critère par défaut codeof
        voisins = Noeud.voisins_noeud(liste_noeuds)  # Dictionnaire des voisins des noeuds
        coloriage = {} # objet qui sera retourné à la fin, il donnera pour chaque couleur ses criteres
        dsat = {noeud : 0 for noeud in voisins.keys()} # permet de suivre le score dsat de chaque noeud
        non_colorie = set(voisins.keys()) # pour avoir un suivi des noeuds non coloriés
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

        # Initialisation pour optimisation des distances
        # On choisit un voisinage plus petit pour la distance entre couleurs
        voisins_directs = Noeud.voisins_noeud(liste_noeuds, max_machine_gap=2, max_time_gap=timedelta(days=4))
        voisins_directs_partition = {}
        for critere, noeuds in partition.items():
            voisins_critere = set()
            for noeud in noeuds:
                voisins_critere.update(voisins_directs[noeud])
            voisins_directs_partition[critere] = voisins_critere
        couleurs_adjacentes_directs = {critere: set() for critere in partition.keys()}

        while non_colorie:
            # Sélection du nœud avec DSAT max (degré max en cas d'égalité)
            noeud_choisi = max(non_colorie, 
                              key=lambda n: (dsat[n], degre[n]))
            
            # On trouve le critère choisi du noeud sélectionné
            critere_choisi = critere_du_noeud[noeud_choisi]
            
            # On cherche les couleurs possibles pour le critère en évitant les couleurs adjacentes
            # car 2 criteres adjacent ne peuvent avoir la meme couleur
            couleurs_possibles = set(coloriage.keys())
            couleurs_possibles.difference_update(couleurs_adjacentes[critere_choisi])

            # On choisit une couleur aléatoire parmi les possibles
            if couleurs_possibles:
                couleur = np.random.choice(list(couleurs_possibles)) # Conversion en liste pour random
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

                    if voisin_du_critere in voisins_directs_partition[critere_choisi]:
                        couleurs_adjacentes_directs[critere_du_voisin].add(couleur)
                    
                    # On met à jour le dsat du voisin du critère
                    dsat[voisin_du_critere] = len(couleurs_adjacentes[critere_du_voisin])

            # On retire tous les noeuds de ce critère de non_colorie
            non_colorie.difference_update(partition[critere_choisi])

        # On va maintenant chercher les couleurs pour optimiser le coloriage
        # On créé un dictionnaire pour regarder la différence de couleur avec ses couleurs
        # voisins pour chaque couleur dans le coloriage

        # On commence par générer le nombre de couleurs nécessaires et les mapper pour faire des
        # opérations sur ces valeurs en coicidant les clés de coloriage et celles ci
        liste_couleurs = generateur_couleur(len(coloriage))
        print(f"La distance minimale de base est \n{evaluer(liste_couleurs)}")
        mapping_couleurs = dict(enumerate(liste_couleurs))
        distance_min_couleurs = {}

        for col, liste_critere in coloriage.items():
            for critere in liste_critere:
                couleurs_voisines = couleurs_adjacentes_directs[critere]
                min_couleur = 100

                # On regarde la différence de couleur entre la couleur cible et ses couleurs voisines
                for couleur_voisine in couleurs_voisines:
                    if couleur_voisine != col:
                        min_nouvelle_couleur = basic_colormath.get_delta_e(
                            mapping_couleurs[col], 
                            mapping_couleurs[couleur_voisine]
                            )

                        # Si la nouvelle couleur est plus proche qu'avant on la remplace
                        if min_nouvelle_couleur < min_couleur:
                            min_couleur = min_nouvelle_couleur
                            distance_min_couleurs[col] = min_nouvelle_couleur
        end = time.time()
        print(f"Durée = {end-start}")
        print(f"La plus petite distance selon le delta e 2000 entre tous les voisins direct est :\n{np.min(list(distance_min_couleurs.values()))}")
        print(f"La moyenne des distances selon le delta e 2000 entre tous les voisins direct est :\n{np.average(list(distance_min_couleurs.values()))}")
        return coloriage


def ecritureFichierColoriage(coloriage, chemin_donnees, choix_critere):
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
    
    with open(chemin_donnees, "r", encoding="utf-8") as f_in, \
         open("ressources/Resultats_planification.txt", "w", encoding="utf-8") as f_out:

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
            couleur = couleur_par_critere.get(str(critere), "")  # vide si pas trouve

            f_out.write(line + ";" + str(couleur) + "\n")
    
if __name__=="__main__":
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
    algo_dsat = DSATUR()
    coloriage = algo_dsat.trouver_coloriage(liste_noeuds=liste_noeuds, critere="codof")
    print(f"Le coloriage est : {coloriage}")
    ecritureFichierColoriage(coloriage, "ressources/Planification.txt", "codof")