from datetime import datetime, timedelta
import tkinter as tk
import colorsys
import pandas as pd


from Noeud import Noeud
from AlgorithmeColoriage import AlgorithmeColoriage
from DSATUR import DSATUR
from DSATUR2 import DSATUR2


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

        self.liste_noeuds = liste_noeuds
        self.partition = Noeud.partition(self.liste_noeuds)
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
        self.header.grid(row=0, column=0, sticky="ew")
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.hbar.grid(row=2, column=0, sticky="ew")
        self.vbar.grid(row=1, column=1, sticky="ns")

        self.grid_rowconfigure([0, 1], weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.coloriage = self.algo_coloriage.trouver_coloriage(
            self.partition, self.voisins
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
                x + 2, 20, anchor="w", text=date.strftime("%d/%m"), font=("Arial", 6)
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
            )
        N = len(self.coloriage.keys())
        hsv_tuples = [(n / N, 0.8, 0.9) for n in range(N)]
        rgb_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        for couleur, critere_par_couleur in self.coloriage.items():
            for critere in critere_par_couleur:
                for noeud in self.partition[critere]:
                    x1 = self.temps_vers_abscisse(noeud.date_debut)
                    x2 = self.temps_vers_abscisse(noeud.date_fin)

                    r, g, b = rgb_tuples[couleur - 1]
                    rgb = (
                        int(r * 255),
                        int(g * 255),
                        int(b * 255),
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
                        f"Prod: {noeud.codeprod}\n"
                        f"OF: {noeud.codeof}\n"
                        f"Sequence: {noeud.sequence}\n"
                        f"Operation: {noeud.codeop}\n"
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
                    text = f"{noeud.codeof} \n {noeud.codeop} \n {noeud.codeprod}"
                    self.canvas.create_text(
                        x1 + 5,
                        y + rect_height / 2,
                        anchor="w",
                        text=text,
                        font=("Arial", 8),
                    )


if __name__ == "__main__":

    data = pd.read_csv("ressources/Planification.txt", sep=";")
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
    algo = DSATUR2()
    diagramme = DiagrammeGant(
        root, liste_noeuds, mapping_machines, algo, max_time_gap=timedelta(days=7)
    )
    diagramme.pack(fill="both", expand=True)

    root.mainloop()
