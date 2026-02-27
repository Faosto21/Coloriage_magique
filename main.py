from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog
import json
import pandas as pd
import sys
from pathlib import Path
from core.Noeud import Noeud
from core.DiagrammeGant import DiagrammeGant
from operators.GenerateurTabulaire import generateur_tabulaire
import os


def get_user_config_path():
    config_dir = Path.home() / "AppData" / "Local" / "Projet_Coloriage"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "path.json"


def browseFiles():
    filename = tk.filedialog.askopenfilename(
        initialdir="/",
        title="Choisir un fichier de données",
        filetypes=(("Text files", "*.txt*"), ("all files", "*.*")),
    )
    with open(get_user_config_path(), "r", encoding="utf-8") as f:
        path = json.load(f)
    if not filename:
        return
    path["planification"] = filename
    planif_path.set(filename)
    with open(get_user_config_path(), "w", encoding="utf-8") as f:
        json.dump(path, f, indent=4)


if __name__ == "__main__":
    if not os.path.exists(get_user_config_path()):
        with open(get_user_config_path(), "w", encoding="utf-8") as f:
            json.dump({"planification": ""}, f, indent=4)
    with open(get_user_config_path(), "r", encoding="utf-8") as f:
        path = json.load(f)
    if (
        path["planification"] == ""
    ):  # Si le chemin n'est pas renseigné, on ouvre la fenêtre de sélection
        fenetre = tk.Tk()
        fenetre.geometry("600x200")
        fenetre.resizable(False, False)
        fenetre.title("Sélection des fichiers de données")

        planif_path = tk.StringVar(value="Pas de fichier sélectionné")
        tk.Label(fenetre, text="Fichier de planification :").grid(row=0, column=0)
        tk.Button(fenetre, text="Parcourir", command=browseFiles).grid(row=0, column=1)
        tk.Button(fenetre, text="Valider", command=fenetre.destroy).grid(
            row=1, column=0, columnspan=2
        )
        tk.Label(
            fenetre,
            textvariable=planif_path,
            wraplength=350,
            anchor="w",
            justify="left",
        ).grid(row=0, column=2)
        fenetre.mainloop()

    # Initialisation des données
    with open(get_user_config_path(), "r", encoding="utf-8") as f:
        path = json.load(f)
    chemin_planification = path["planification"]
    # Initialisation des données
    chemin_planification_modifiee, chemin_machine_modifiee = generateur_tabulaire(
        chemin_planification, get_user_config_path().parent
    )

    data = pd.read_csv(chemin_planification_modifiee, dtype=str, sep=";")
    machines = pd.read_csv(chemin_machine_modifiee)
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

    # Initialisation des objets
    root = tk.Tk()
    root.title("Diagramme de Gant")
    # Dimension de la fenêtre pour que seulement 7 lignes et 7 jours soit visibles.
    root.geometry("1000x700")
    root.resizable(False, False)
    diagramme = DiagrammeGant(
        root,
        liste_noeuds=liste_noeuds,
        map_machines=mapping_machines,
        max_time_gap=timedelta(days=7),
        chemin_entree=chemin_planification,
        chemin_sortie=get_user_config_path().parent / "Resultats_planification.txt",
    )
    diagramme.pack(fill="both", expand=True)

    # Lancement du script
    root.mainloop()
