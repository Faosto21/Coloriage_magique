import tkinter as tk
import json
import os
from pathlib import Path

from core.Noeud import Noeud
from core.DiagrammeGantt import DiagrammeGantt, fenetre_chemin


def get_user_config_path() -> Path:
    """
    Retourne le chemin du fichier de configuration de l'utilisateur. Si le fichier n'existe pas, il est créé avec une configuration par défaut.
    :return: Path vers le fichier de configuration de l'utilisateur"""
    config_dir = Path.home() / "AppData" / "Local" / "Projet_Coloriage"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "path.json"


if __name__ == "__main__":
    if not os.path.exists(
        get_user_config_path()
    ):  # Creation du fichier de config s'il n'existe pas
        with open(get_user_config_path(), "w", encoding="utf-8") as f:
            json.dump({"planification": ""}, f, indent=4)
    with open(get_user_config_path(), "r", encoding="utf-8") as f:
        path = json.load(f)
    root = tk.Tk()
    root.geometry("100x100")
    if (
        path["planification"] == ""
    ):  # Si le chemin n'est pas renseigné, on ouvre la fenêtre de sélection
        fenetre_chemin(root, get_user_config_path(), None)
    # Initialisation des données
    with open(get_user_config_path(), "r", encoding="utf-8") as f:
        path = json.load(f)
    chemin_planification = Path(path["planification"])
    liste_noeuds, mapping_machines = Noeud.creation_noeuds(
        chemin_planification,
        get_user_config_path().parent,  # Creation des noeuds et du mapping_machine
    )

    # Initialisation des objets
    root.title("Diagramme de Gantt")
    # Dimension de la fenêtre pour que seulement 7 lignes et 7 jours soit visibles.
    root.geometry("1000x700")
    root.resizable(False, False)
    diagramme = DiagrammeGantt(
        root,
        liste_noeuds=liste_noeuds,
        map_machines=mapping_machines,
        chemin_entree=chemin_planification,
        chemin_path=get_user_config_path(),
        chemin_sortie=get_user_config_path().parent / "Resultats_planification.txt",
    )
    diagramme.pack(fill="both", expand=True)

    # Lancement du script
    root.mainloop()
