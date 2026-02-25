from datetime import datetime, timedelta
import tkinter as tk
import pandas as pd
from pathlib import Path
from core.Noeud import Noeud
from core.DiagrammeGant import DiagrammeGant
from operators.AlgorithmeColoriage import DSATUR
from operators.WelshPowell import WelshPowell
from operators.GenerateurTabulaire import generateur_tabulaire
import os 

if __name__ == "__main__":
    # Chemin vers dossier parent
    chemin_dossier = Path(os.path.dirname(__file__))
    chemin_planification = Path(os.path.join(chemin_dossier, "ressources/Planification.txt"))
    chemin_machine = Path(os.path.join(chemin_dossier, "ressources/Machine.txt"))
    chemin_planification_modifiee = os.path.join(chemin_dossier, "ressources/Planification_modifiee.txt")
    chemin_machine_modifiee = os.path.join(chemin_dossier, "ressources/Machine_modifiee.txt")

    # Initialisation des données
    generateur_tabulaire(
        chemin_planification
    )  # On modifie Planning et Machine en cherchant les chevauchements
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
    algo = DSATUR()
    diagramme = DiagrammeGant(
        root, liste_noeuds, mapping_machines, algo, max_time_gap=timedelta(days=7)
    )
    diagramme.pack(fill="both", expand=True)

    # Lancement du script
    root.mainloop()