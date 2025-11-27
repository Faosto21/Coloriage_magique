from datetime import datetime, timedelta
import tkinter as tk
import pandas as pd
from Noeud import Noeud


class DiagrammeGant(tk.Frame):
    """
    Classe permettant de visualiser le diagramme de Gant
    """

    def __init__(
        self,
        fenetre,
        liste_noeuds: list[Noeud],
        map_machines: dict[str, int],
        pixels_per_hour=20,
    ):
        super().__init__(fenetre)

        self.liste_noeuds = liste_noeuds
        self.map_machines = map_machines
        self.pixels_per_hour = pixels_per_hour

        # Canvas + Scrollbars
        self.canvas = tk.Canvas(self, bg="white", width=900, height=600)
        self.hbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.vbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(
            xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set
        )

        # Layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.hbar.grid(row=1, column=0, sticky="ew")
        self.vbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.dessine()

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
        return delta_h * self.pixels_per_hour

    def dessine(self):
        """
        Dessine chaque Noeud dans le canvas

        :param self: Description
        """
        # Déterminer l'intervalle de temps
        self.min_date = min(noeud.date_debut for noeud in self.liste_noeuds)
        self.max_date = max(noeud.date_fin for noeud in self.liste_noeuds)

        lane_height = 50
        rect_height = 30

        for centre, i in self.map_machines.items():
            noeuds_par_centre = [
                noeud for noeud in self.liste_noeuds if noeud.centre == centre
            ]
            y = 20 + i * lane_height
            # Label pour chaque centre , !! à mieux placer
            self.canvas.create_text(
                10,
                y + rect_height / 2,
                anchor="w",
                text=centre,
                font=("Arial", 11, "bold"),
            )

            for noeud in noeuds_par_centre:
                x1 = self.temps_vers_abscisse(noeud.date_debut)
                x2 = self.temps_vers_abscisse(noeud.date_fin)

                # Dessin du rectangle , choix de la couleur ici
                self.canvas.create_rectangle(
                    x1, y, x2, y + rect_height, fill="skyblue", outline="black"
                )

                # Avec le texte à l'intérieur
                self.canvas.create_text(
                    x1 + 5,
                    y + rect_height / 2,
                    anchor="w",
                    text=noeud.codeof,
                    font=("Arial", 10),
                )

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


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
    print(len(partition))  # 108 valeurs différentes de codeof

    root = tk.Tk()
    root.title("Diagramme de Gant")
    diagramme = DiagrammeGant(root, liste_noeuds, mapping_machines)
    diagramme.pack(fill="both", expand=True)

    root.mainloop()
