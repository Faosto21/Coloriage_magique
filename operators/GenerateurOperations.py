from pathlib import Path
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk


def fenetre_generer_planification(root):
    """
    Ouvre une fenêtre pour générer une planification aléatoire avec des paramètres personnalisables.
    Permet à l'utilisateur de choisir le chemin de sortie du fichier généré et les paramètres de la planification.
        :param root: la fenêtre principale de l'application, nécessaire pour créer une fenêtre modale
    """

    def generer():
        nb_lignes = int(nb_lignes_entry.get())
        nb_centres = int(nb_centres_entry.get())
        nb_produits = int(nb_produits_entry.get())
        duree_max_jours = int(duree_max_jours_entry.get())
        generer_planification(
            nb_lignes=nb_lignes,
            nb_centres=nb_centres,
            nb_produits=nb_produits,
            duree_max_jours=duree_max_jours,
            chemin_sortie=planif_path.get(),
        )
        fenetre.destroy()

    def browse_file():
        file_path = filedialog.asksaveasfilename(
            title="Enregistrer la planification générée",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            planif_path.set(file_path)

    fenetre = tk.Toplevel(root)
    fenetre.title("Générer une planification")
    fenetre.geometry("400x600")

    tk.Label(fenetre, text="Chemin de sortie :").pack(pady=5)
    planif_path = tk.StringVar(value="Pas de chemin sélectionné")
    tk.Label(fenetre, textvariable=planif_path, wraplength=350).pack(pady=5)

    tk.Button(
        fenetre,
        text="Parcourir",
        command=browse_file,
    ).pack(pady=5)

    tk.Label(fenetre, text="Nombre de lignes :").pack(pady=5)
    nb_lignes_entry = tk.Entry(fenetre)
    nb_lignes_entry.pack(pady=5)

    tk.Label(fenetre, text="Nombre de centres :").pack(pady=5)
    nb_centres_entry = tk.Entry(fenetre)
    nb_centres_entry.pack(pady=5)

    tk.Label(fenetre, text="Nombre de produits :").pack(pady=5)
    nb_produits_entry = tk.Entry(fenetre)
    nb_produits_entry.pack(pady=5)

    tk.Label(fenetre, text="Durée max (jours) :").pack(pady=5)
    duree_max_jours_entry = tk.Entry(fenetre)
    duree_max_jours_entry.pack(pady=5)

    generer_btn = ttk.Button(fenetre, text="Générer", command=generer)
    generer_btn.pack(pady=20)


def generer_planification(
    nb_lignes: int,
    nb_centres: int = 30,
    nb_produits: int = 30,
    duree_max_jours: int = 180,  # 6 mois par défaut
    chemin_sortie: str = "/ressources/Planification.txt",
):
    """
    Genère un fichier de planification aléatoire avec les paramètres spécifiés. \n

    Les centres sont générés aléatoirement avec des préfixes "MAC", "POSTE" ou "LIGNE". \n
    Les produits sont générés aléatoirement avec des préfixes "PROD", "P", "REF" ou "PRODMO". \n
    Les opérations sont générées avec des codes "OF" pour les machines et "AF" pour les autres centres. \n
    Les dates de début et de fin sont générées aléatoirement avec une durée entre 30 minutes et 72 heures, et une date de début dans les 30 derniers jours. \n
    :param nb_lignes: le nombre de lignes (opérations) à générer dans le fichier de planification
    :param nb_centres: le nombre de centres différents à générer (par défaut 30)
    :param nb_produits: le nombre de produits différents à générer (par défaut 30)
    :param duree_max_jours: la durée maximale en jours entre la date de début et la date de fin des opérations (par défaut 180 jours)
    :param chemin_sortie: le chemin du fichier de planification généré (par défaut "/ressources/Planification.txt")
    """
    import random
    from datetime import datetime, timedelta
    import csv

    # Générer les centres
    centres = []
    types_centre = ["MAC", "POSTE", "LIGNE"]
    for i in range(1, nb_centres + 1):
        type_c = random.choice(types_centre)
        if type_c == "MAC":
            num = random.randint(101, 599)
            centres.append(f"MAC{num}")
        elif type_c == "POSTE":
            num = random.randint(1, 20)
            centres.append(f"POSTE{num}")
        else:
            num = random.randint(1, 15)
            centres.append(f"LIGNE{num}")
    centres = list(set(centres))  # Supprimer les doublons

    # Générateur de produits (codprod)
    produits = []
    prefixes = ["PROD", "P", "REF", "PRODMO"]
    for i in range(1, nb_produits + 1):
        prefix = random.choice(prefixes)
        if prefix == "PROD":
            num = random.randint(1, 30)
            if random.random() < 0.3:
                produits.append(f"PROD{num:02d}V{random.randint(1,3)}")
            else:
                produits.append(f"PROD{num:02d}")
        elif prefix == "P":
            produits.append(f"P{random.randint(1,20):02d}")
        elif prefix == "REF":
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

    with open(chemin_sortie, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(
            ["centre", "codprod", "codof", "sequence", "codop", "dtedeb", "dtefin"]
        )

        ligne_actuelle = 0
        while ligne_actuelle < nb_lignes:
            centre = random.choice(centres)
            nb_ops = random.randint(2, 20)

            date_courante = date_debut + timedelta(
                days=random.randint(0, duree_max_jours),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            for i in range(nb_ops):
                if ligne_actuelle >= nb_lignes:
                    break

                codprod = random.choice(produits)

                if centre.startswith("MAC"):
                    codof = generer_code("OF", centre)
                else:
                    codof = generer_code("AF", centre)

                sequence = f"{random.randint(0, 5):04d}"
                codop = random.choice(operations)

                # Durée entre 30 minutes et 72 heures
                duree_heures = random.uniform(0.5, 72)
                date_fin = date_courante + timedelta(hours=duree_heures)

                writer.writerow(
                    [
                        centre,
                        codprod,
                        codof,
                        sequence,
                        codop,
                        date_courante.strftime("%Y-%m-%d %H:%M:%S.000"),
                        date_fin.strftime("%Y-%m-%d %H:%M:%S.000"),
                    ]
                )

                ligne_actuelle += 1
                date_courante = date_fin


# Utilisation
if __name__ == "__main__":
    # 10 000 ope
    chemin_dossier = Path(os.path.dirname(__file__)).parent
    chemin_sortie = os.path.join(chemin_dossier, "ressources", "Planification_test.txt")
    generer_planification(
        nb_lignes=10000,
        nb_centres=10,
        nb_produits=100,
        duree_max_jours=365,  # 1 an max
        chemin_sortie=chemin_sortie,
    )
