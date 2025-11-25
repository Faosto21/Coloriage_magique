import pandas as pd
import datetime

# transformation du .txt en dataframe
data = pd.read_csv("DataPlanification.txt", sep=";")

# on regarde pour l'instant les 5 premieres valeurs
data
print(data)

# création des noeuds et du critère
noeuds = []
# on s'intéresse à un critère précis selon comment ce qu'on veut regrouper/colorier
critere = data["codof"] # ici on regarde le codof, ca servira de critere d'équivalence entre 2 noeud

for i in range(len(data["centre"])):
    noeuds.append((
        (data["dtedeb"][i], data["dtefin"][i]), 
         (data["centre"][i], str(data["codprod"][i]) + str(data["codof"][i]) +str(data["sequence"][i]) + str(data["codof"][i])),
         critere[i]
        ))

print(f"Exemple de 2 noeuds : \n{noeuds[0]}\n{noeuds[1]}")

def partitionner_noeuds(noeuds):
    """
    Va prendre tous les noeuds (toutes les lignes du dataframe initial en soit) et les rassembler s'ils
    vérifient le même critère, on obtient alors un dictionnaire avec en clé les critères et en valeur 
    la liste des noeuds qui vérifie le critère associé
    """
    partition = {}
    for noeud in noeuds:
        clé = noeud[2]
        if clé in partition:
            partition[clé].append(noeud)
        else:
            partition[clé] = [noeud]
    return partition

partition = partitionner_noeuds(noeuds)
print(f"\nExemple d'une clé/valeur de la partition obtenue : {list(partition.items())[0]}")
print(f"Vérifions le nombre de clé obtenue : {len(partition.keys())}")

# On obtient 47, càd que sur les 100 noeuds de base, il y'a 47 codof différents

for value in list(partition.values())[25:30]:
    print(f"La longueur de la valeur est : {len(value)}")