from ast import Return
import colorsys
import tkinter as tk
import itertools

def show_colors(rgb_tuples):
    root = tk.Tk()
    root.title("Visualisation couleurs")
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame, width=600, height=300)
    canvas.grid(row=0, column=0, sticky="nsew")

    scroll_bar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scroll_bar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scroll_bar.set)

    box_height = 15
    x0, x1 = 10, 300

    for i, (r, g, b) in enumerate(rgb_tuples):
        hex_color = "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))

        y0 = 10 + i * (box_height + 5)
        y1 = y0 + box_height

        canvas.create_rectangle(x0, y0, x1, y1, fill=hex_color, outline="black")
        canvas.create_text(350, (y0 + y1) // 2, text=i)

    canvas.configure(scrollregion=canvas.bbox("all"))

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    root.mainloop()


def evaluer_coloriage(coloriage : dict[int, set[str]]) -> float:
    """
    Fonction qui prend en paramètre un coloriage 
    Et qui renvoie un score qui évalue le coloriage
    
    :param coloriage: resultat d'un algorithme de coloriage
    :type coloriage: dict[int, set[str]]
    :param voisins: dico avec chaque noeud en clé et l'ensemble des voisins du noeud en valuer
    :type voisins: dict[int, set[str]]
    :return: Score du coloriage
    :rtype: float
    """
    couleurs_voisines = {} # dictionnaire qui contient les couleurs en cle et l'ensemble de ces couleurs voisines en valeur

    score = float('inf')
    for couleur in couleurs_voisines:
        if couleurs_voisines[couleur]:
            score = min(score, min(abs(couleur - v) for v in couleurs_voisines[couleur]))

    if score == float('inf'):
        score = 0
    
    return score 


def choix_coloriage(coloriage : dict[int, set[str]]) -> dict[int, set[str]]:
    """
    Fonction qui prend en paramètre un coloriage issue d'un algorithme de coloriage
    Et qui renvoie le meilleur coloriage 
    
    :param coloriage : resultat d'un algorithme de coloriage
    :type coloriage :dict[int, set[str]]
    :return: meilleur coloriage (celui qui maximise la différence entre des couleurs voisines)
    :rtype: dict[int, set[str]]
    """
    # Initialisation des variables
    couleurs_voisines = {} # dictionnaire qui contient les couleurs en cle et l'ensemble de ces couleurs voisines en valeur
    couleurs = list(coloriage.keys())
    valeurs  = list(coloriage.values())
    meilleur_coloriage = coloriage
    meilleur_score = evaluer_coloriage(coloriage)

    # On teste les permutations
    for sigma in itertools.permutations(valeurs):
        nouveau = {couleurs[i]: sigma[i] for i in range(len(couleurs))}
        score = evaluer_coloriage(nouveau)

        if score > meilleur_score:
            meilleur_coloriage = nouveau
            meilleur_score = score

    return meilleur_coloriage



if __name__ == "__main__":
    #N = 50  # Nombre de couleurs
    #hsv_tuples = [(n / N, 0.8, 0.9) for n in range(N)]
    #rgb_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    #show_colors(rgb_tuples)

    coloriage_test = {1 : {"val_critere1", "val_critere2"}, 2 : {"val_critere3"}, 3 : {"val_critere4"}}
    print(evaluer_coloriage(coloriage_test))
