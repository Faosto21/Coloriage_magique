from pathlib import Path
import os

def generer_planification(
    nb_lignes: int,
    nb_centres: int = 30,
    nb_produits: int = 30,
    duree_max_jours: int = 180,  # 6 mois par défaut
    chemin_sortie: str = "/ressources/Planification.txt"
):
    """
    Version avec paramètres ajustables
    """
    import random
    from datetime import datetime, timedelta
    import csv
    
    # Générer les centres
    centres = []
    types_centre = ['MAC', 'POSTE', 'LIGNE']
    for i in range(1, nb_centres + 1):
        type_c = random.choice(types_centre)
        if type_c == 'MAC':
            num = random.randint(101, 599)
            centres.append(f"MAC{num}")
        elif type_c == 'POSTE':
            num = random.randint(1, 20)
            centres.append(f"POSTE{num}")
        else:
            num = random.randint(1, 15)
            centres.append(f"LIGNE{num}")
    centres = list(set(centres))  # Supprimer les doublons
    
    # Générateur de produits (codprod)
    produits = []
    prefixes = ['PROD', 'P', 'REF', 'PRODMO']
    for i in range(1, nb_produits + 1):
        prefix = random.choice(prefixes)
        if prefix == 'PROD':
            num = random.randint(1, 30)
            if random.random() < 0.3:
                produits.append(f"PROD{num:02d}V{random.randint(1,3)}")
            else:
                produits.append(f"PROD{num:02d}")
        elif prefix == 'P':
            produits.append(f"P{random.randint(1,20):02d}")
        elif prefix == 'REF':
            produits.append(f"REF{random.randint(1,15):02d}")
        else:
            produits.append(f"PRODMO{random.randint(1,8)}")
    
    operations = [f"{i:04d}" for i in range(10, 100, 10)]
    
    # Générateur de codes
    compteurs = {}
    
    def generer_code(prefix, centre):
        key = f"{prefix}_{centre}"
        compteurs[key] = compteurs.get(key, 0) + 1
        return f"{prefix}{compteurs[key]:08d}"
    
    # Date de départ (aujourd'hui - 1 mois pour avoir du passé et du futur)
    date_debut = datetime.now() - timedelta(days=30)
    
    with open(chemin_sortie, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['centre', 'codprod', 'codof', 'sequence', 'codop', 'dtedeb', 'dtefin'])
        
        ligne_actuelle = 0
        while ligne_actuelle < nb_lignes:
            centre = random.choice(centres)
            nb_ops = random.randint(2, 20)
            
            date_courante = date_debut + timedelta(
                days=random.randint(0, duree_max_jours),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            for i in range(nb_ops):
                if ligne_actuelle >= nb_lignes:
                    break
                
                codprod = random.choice(produits)
                
                if centre.startswith('MAC'):
                    codof = generer_code("OF", centre)
                else:
                    codof = generer_code("AF", centre)
                
                sequence = f"{random.randint(0, 5):04d}"
                codop = random.choice(operations)
                
                # Durée entre 30 minutes et 72 heures
                duree_heures = random.uniform(0.5, 72)
                date_fin = date_courante + timedelta(hours=duree_heures)
                
                writer.writerow([
                    centre, codprod, codof, sequence, codop,
                    date_courante.strftime("%Y-%m-%d %H:%M:%S.000"),
                    date_fin.strftime("%Y-%m-%d %H:%M:%S.000")
                ])
                
                ligne_actuelle += 1
                date_courante = date_fin

# Utilisation
if __name__ == "__main__":
    # 50 000 ope
    chemin_dossier = Path(os.path.dirname(__file__)).parent
    chemin_sortie = os.path.join(chemin_dossier, "ressources", "Planification.txt")
    generer_planification(
        nb_lignes=10000,
        nb_centres=40,
        nb_produits=40,
        duree_max_jours=365,  # 1 an max
        chemin_sortie=chemin_sortie
    )