from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
import pandas as pd
import time
from pathlib import Path

from operators.GenerateurCouleur import generateur_couleur
from core.Noeud import Noeud
from operators.AlgorithmeColoriage import AlgorithmeColoriage
from operators.AlgorithmeColoriage import DSATUR
from operators.GenerateurTabulaire import generateur_tabulaire


class CanvasTooltip:
    """
    Classe pour afficher les attributs d'un noeud quand on hover sur la case.
    """

    def __init__(self, canvas, text):
        self.canvas = canvas
        self.text = text
        self.tip = None

    def show(self, x, y):
        if self.tip:
            return
        self.tip = tk.Toplevel(self.canvas)
        self.tip.wm_overrideredirect(True)

        label = tk.Label(
            self.tip,
            text=self.text,
            background="lightyellow",
            foreground="black",
            relief="solid",
            borderwidth=1,
            padx=5,
            pady=2,
            font=("Tahoma", 8),
        )
        label.pack()

        self.tip.wm_geometry(f"+{x+15}+{y+15}")

    def hide(self):
        if self.tip:
            self.tip.destroy()
        self.tip = None


class DiagrammeGant(tk.Frame):
    """
    Classe permettant de visualiser le diagramme de Gant tout en trouvant un coloriage.
    Atttributs :
        -listes_noeuds (list[Noeud]) : La liste de tous les noeuds (opérations) qui vont être affichés dans le diagramme.
        -map_machines (dict[str,int]) : Dictionnaire qui associe chaque centre à son indice dans Machine.txt et donc sa ligne dans le diagramme.
        -algo_coloriage (AlgorithmeColoriage) : Algorithme de coloriage utilisé pour trouver le nombre de couleurs différentes utilisés dans le diagramme.
        -max_machine_gap (int) : Ecart maximum en indice de centre pour être considéré voisins.
        -max_time_gap (timedelta) : Ecart maximum de temps pour être considéré voisins.

    """

    def __init__(
        self,
        fenetre,
        liste_noeuds: list[Noeud],
        map_machines: dict[str, int],
        algo_coloriage: AlgorithmeColoriage,
        max_machine_gap: int = 3,
        max_time_gap: timedelta = timedelta(days=21),
    ):
        super().__init__(fenetre)

        # Barre de contrôle (au-dessus du header)
        self.controls = tk.Frame(self)
        self.controls.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.grid_columnconfigure(0, weight=1)

        tk.Label(self.controls, text="Critère :", font=("Arial", 10)).pack(side="left")

        self.critere_var = tk.StringVar(value="codop")
        self.critere_box = ttk.Combobox(
            self.controls,
            textvariable=self.critere_var,
            values=Noeud.criteres_partition,
            state="readonly",
            width=12,
        )
        self.critere_box.pack(side="left", padx=5)

        self.valider_btn = ttk.Button(
            self.controls, text="Valider", command=self.on_change_critere
        )
        self.valider_btn.pack(side="left", padx=5)

        self.liste_noeuds = liste_noeuds
        # Partition initiale selon le critère sélectionné
        self.partition = Noeud.partition(
            self.liste_noeuds, critere=self.critere_var.get()
        )
        self.voisins = Noeud.voisins_noeud(
            self.liste_noeuds, max_machine_gap, max_time_gap
        )
        self.map_machines = map_machines
        self.algo_coloriage = algo_coloriage

        self.pixels_per_hour = 5

        # Canvas + Scrollbars
        self.header = tk.Canvas(self, height=40, bg="lightgray")
        self.canvas = tk.Canvas(self, bg="white", width=900, height=600)
        self.hbar = tk.Scrollbar(self, orient="horizontal", command=self.scroll_both)
        self.vbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.header.configure(xscrollcommand=self.hbar.set)
        self.canvas.configure(
            xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set
        )

        # Layout
        self.header.grid(row=1, column=0, sticky="ew")
        self.canvas.grid(row=2, column=0, sticky="nsew")
        self.hbar.grid(row=3, column=0, sticky="ew")
        self.vbar.grid(row=2, column=1, sticky="ns")

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.coloriage = self.algo_coloriage.trouver_coloriage(
            self.liste_noeuds, self.critere_var.get()
        )
        self.dessine()

        # Ajustement des scroll_region pour éviter le décalage entre la time line et les opérations
        main_bbox = self.canvas.bbox("all")
        xmin, _, xmax, _ = main_bbox
        self.canvas.configure(scrollregion=main_bbox)
        self.header.configure(scrollregion=(xmin, 0, xmax, 40))

    def scroll_both(self, *args):
        """
        Permet de scroll à la fois le header( ligne de temps) et le canva(diagramme avec les noeuds) avec la scroll_bar horizontale.

        :param self: Description
        :param args: Description
        """
        self.header.xview(*args)
        self.canvas.xview(*args)

    def temps_vers_abscisse(self, date: datetime) -> float:
        """
        Convertit une date en abscisse

        :param self: Description
        :param date: Date de début ou de fin d'un Noeud
        :type date: datetime
        :return: Coordonnées dans le Canvas
        :rtype: float
        """
        delta_h = (date - self.min_date).total_seconds() / 3600
        return delta_h * self.pixels_per_hour + 90

    def dessine(self):
        """
        Dessine le diagramme de Gant en dessinant la ligne de temps au dessus puis tous les noeuds en dessous.

        :param self: Description
        """
        self.min_date = min(noeud.date_debut for noeud in self.liste_noeuds)
        self.max_date = max(noeud.date_fin for noeud in self.liste_noeuds)

        self.dessine_ligne_de_temps()
        self.dessine_noeud()

    def on_change_critere(self, event=None):
        critere = self.critere_var.get()

        # Recalcule la partition et le coloriage avec le nouveau critère
        self.partition = Noeud.partition(self.liste_noeuds, critere=critere)

        # self.voisins ne dépend pas du critère (voisinage entre noeuds)
        # On passe la liste de noeuds et la valeur du critère à l'algorithme
        self.coloriage = self.algo_coloriage.trouver_coloriage(
            self.liste_noeuds, critere
        )

        # Redessine
        self.dessine()

        # Remet à jour les scrollregions (comme dans __init__)
        main_bbox = self.canvas.bbox("all")
        if main_bbox:
            xmin, _, xmax, _ = main_bbox
            self.canvas.configure(scrollregion=main_bbox)
            self.header.configure(scrollregion=(xmin, 0, xmax, 40))

    def dessine_ligne_de_temps(self):
        """
        Dessine la barre du temps au dessus du diagramme.

        :param self: Description
        """
        ## !!! A finir, echelle de temps décalé par rapport aux opérations
        self.header.delete("all")
        start = datetime(self.min_date.year, self.min_date.month, self.min_date.day)
        date = start

        while date <= self.max_date:
            x = self.temps_vers_abscisse(date)
            self.header.create_line(x, 0, x, 40)
            self.header.create_text(
                x + 2,
                20,
                anchor="w",
                text=date.strftime("%d/%m"),
                font=("Arial", 6),
                fill="black",
            )
            date += timedelta(days=1)

    def dessine_noeud(self):
        """
        Dessine chaque Noeud du diagramme

        :param self: Description
        """
        self.canvas.delete("all")
        lane_height = 80
        rect_height = 80

        for centre, i in self.map_machines.items():
            y = 20 + i * lane_height
            # Label pour chaque centre ,
            self.canvas.create_text(
                10,
                y + rect_height / 2,
                anchor="w",
                text=centre,
                font=("Arial", 11, "bold"),
                fill="black",
            )
        N = len(self.coloriage.keys())
        rgb_tuples = list(generateur_couleur(N))
        for couleur, critere_par_couleur in self.coloriage.items():
            for critere in critere_par_couleur:
                for noeud in self.partition[critere]:
                    x1 = self.temps_vers_abscisse(noeud.date_debut)
                    x2 = self.temps_vers_abscisse(noeud.date_fin)

                    r, g, b = rgb_tuples[couleur - 1]
                    rgb = (
                        int(r),
                        int(g),
                        int(b),
                    )
                    y = 20 + self.map_machines[noeud.centre] * lane_height
                    hex_color = "#%02x%02x%02x" % rgb

                    # Dessin du rectangle
                    rectangle = self.canvas.create_rectangle(
                        x1,
                        y,
                        x2,
                        y + rect_height,
                        fill=hex_color,
                        outline="black",
                    )

                    # Et ajout des informations quand on hover
                    tooltip_text = (
                        f"Centre: {noeud.centre}\n"
                        f"Prod: {noeud.codprod}\n"
                        f"OF: {noeud.codof}\n"
                        f"Sequence: {noeud.sequence}\n"
                        f"Operation: {noeud.codop}\n"
                        f"Start: {noeud.date_debut}\n"
                        f"End: {noeud.date_fin}"
                    )
                    tooltip = CanvasTooltip(self.canvas, tooltip_text)

                    self.canvas.tag_bind(
                        rectangle,
                        "<Enter>",
                        lambda e, t=tooltip: t.show(e.x_root, e.y_root),
                    )
                    self.canvas.tag_bind(
                        rectangle, "<Leave>", lambda e, t=tooltip: t.hide()
                    )

                    # Avec le texte à l'intérieur
                    text = f"{noeud.codof} \n {noeud.codop} \n {noeud.codprod}"
                    self.canvas.create_text(
                        x1 + 5,
                        y + rect_height / 2,
                        anchor="w",
                        text=text,
                        font=("Arial", 8),
                        fill="black",
                    )


if __name__ == "__main__":
    generateur_tabulaire(
        Path("ressources/Planification.txt"), Path("ressources/Machine.txt")
    )  # On modifie Planning et Machine en cherchant les chevauchements
    data = pd.read_csv("ressources/Planification_modifiee.txt", dtype=str, sep=";")
    machines = pd.read_csv("ressources/Machine_modifie.txt")
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
        liste_noeuds
    )  # Partition de la liste de noeud selon le critère par défaut codeof
    voisins = Noeud.voisins_noeud(liste_noeuds)  # Dictionnaire des voisins des noeuds
    voisins_partition = {
        critere: set.union(
            *[voisins[noeud] for noeud in noeuds]
        )  # Dictionnaires des voisins de chaque partie de partition
        for critere, noeuds in partition.items()
    }
    # print(len(partition))  # 108 valeurs différentes de codeof

    root = tk.Tk()
    root.title("Diagramme de Gant")
    algo = DSATUR()
    diagramme = DiagrammeGant(
        root, liste_noeuds, mapping_machines, algo, max_time_gap=timedelta(days=7)
    )
    diagramme.pack(fill="both", expand=True)

    root.mainloop()
