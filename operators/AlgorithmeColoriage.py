from abc import abstractmethod, ABC
from typing import List
from core.Noeud import Noeud
import numpy as np
import time
from datetime import timedelta
from operators.GenerateurCouleur import generateur_couleur, evaluer
import basic_colormath

class AlgorithmeColoriage(ABC):
    """
    Classe abstraite d'algorithme de coloriage
    """

    @abstractmethod
    def trouver_coloriage(
        self, 
        liste_noeuds : List[Noeud], 
        critere: str
        ) -> dict[int, set[str]]:
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
        :return: Dictionnaire dont les clés sont le numéro de couleur et la valeur la liste des valeurs de critères qui seront coloriés de cette couleur
        :rtype: dict[tuple[float, float,float], set[str]]
        """

class DSATUR(AlgorithmeColoriage):
    """
    Algorithme de DSATUR
    """
    def trouver_coloriage(
            self,
            liste_noeuds : List[Noeud],
            critere : str
            ) -> dict[tuple[float, float,float], set[str]]:
        
        # Initialisation
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

            # On choisit une couleur aléatoire pour le critere parmi les possibles
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
                    
                    # On met à jour le dsat du voisin du critère
                    dsat[voisin_du_critere] = len(couleurs_adjacentes[critere_du_voisin])

            # On retire tous les noeuds de ce critère de non_colorie
            non_colorie.difference_update(partition[critere_choisi])

        # On va maintenant attribuer les couleurs générées à chaque clé de notre coloriage
        liste_couleurs = generateur_couleur(len(coloriage))
        dico_couleurs = dict(enumerate(liste_couleurs))

        # On transforme les np.array en tuple pour qu'ils soient hashables et les mettre en clé
        dico_couleurs_tuple = {key : tuple(arr) for key, arr in dico_couleurs.items()}

        # On obtient le dictionnaire avec clé = couleur RGB et valeur = ensemble des noeuds de cette couleur
        coloriage_final = {couleur_rgb : coloriage[numero] for numero, couleur_rgb in dico_couleurs_tuple.items()}

        return coloriage_final


def ecritureFichierColoriage(coloriage : dict[tuple[float, float, float] : set[str]], 
                             chemin_donnees : str, 
                             choix_critere : str
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