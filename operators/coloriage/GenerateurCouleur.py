""" 
Ce fichier sert à générer les couleurs de manière optimale en utilisant la distance delta e 2000
Le but est d'en générer 10 fois trop et ensuite de choisir de manière à maximiser la distance 
entre toutes les couleurs 2 à 2 et garantir un résultat visuel optimal
On considère que 2 couleurs sont différentes avec un score entre 5 et 10 
et sont complètement différentes si score > 10. 
On obtient pour 50 couleurs environ 9.3 ce qui est très bien
"""

import numpy as np
import basic_colormath
import tkinter as tk
from typing import Annotated
from numpy.typing import NDArray

RGBArray = Annotated[
    NDArray[np.float64],
    "Shape: (n, 3), Range: [0, 255]"
]

def generateur_rgb(
        n: int,
        range_saturation : tuple[float, float] = (20,80), # Saturation pour pastel
        range_lightness : tuple[float, float] = (50,75) # Luminosité moyenne pour éviter blanc/noir
        ) -> RGBArray:
    """
    Fonction pour générer n couleurs en format RGB. On génère en premier les couleurs sous
    format HSL car permet de générer plus uniformément que dans l'espace RGB. On pourrait
    également utiliser l'espace LAB spécialement conçu pour, mais cet espace donne des résultats très satisfaisant
    et est plus simple à comprendre.

    Args:
        n (int): nombre de couleurs que l'on souhaite générer
        range_saturation (tuple[float, float]): le min et le max de la saturation que l'on souhaite dans l'espace HSL
        range_lightness (tuple[float, float]): le min et le max de la lightness que l'on souhaite dans l'espace HSL

    Returns:
        RGBArray: Tableau de couleurs RGB 
    """
    min_saturation = range_saturation[0]
    max_saturation = range_saturation[1]
    min_lightness = range_lightness[0]
    max_lightness = range_lightness[1]

    # On génère n couleurs en HSL pour avoir des couleurs optimales
    hues = np.linspace(0, 365, n, endpoint=False) % 365 # Uniformité en teinte sur le disque
    saturation = np.random.uniform(min_saturation, max_saturation, n) 
    lightness = np.random.uniform(min_lightness, max_lightness, n) 
    hsl_colors = np.column_stack([hues, saturation, lightness])
 
    return basic_colormath.hsls_to_rgb(hsl_colors)

def maximin_delta_e2000(
        candidats: RGBArray, 
        n: int
        ) -> RGBArray:
    """Sélectionne n couleurs maximisant la distance Delta E 2000.

    Args:
        candidats (RGBArray): "liste" de candidats pour obtenir une nouvelle "liste" ayant la plus grande distance 2 à 2.
        n (int): nombre de couleurs que l'on souhaite obtenir

    Returns:
        RGBArray: Notre RGBArray contenant les n couleurs parmi les candidats qui maximisent la distance 2 à 2.
    """
    
    # On choisit une première couleur aléatoire
    first_idx = np.random.randint(0, len(candidats))
    couleurs_choisies = candidats[[first_idx]]
    candidats_disponibles = np.delete(candidats, first_idx, axis=0)
    
    # Initialisation de la matrice des distances minimales
    min_distances = np.full(len(candidats_disponibles), np.inf)
    
    # On remplit jusqu'à avoir n couleurs
    for _ in range(n - 1):
        # On calcule les distances vers la dernière couleur choisie
        new_distances = basic_colormath.get_delta_e_matrix(
            couleurs_choisies[[-1]],  # Dernière couleur choisie
            candidats_disponibles
        ).flatten() # flatten pour faciliter les opérations suivantes et éviter np.where...
        
        # On met à jour les distances minimales entre toutes les couleurs
        min_distances = np.minimum(min_distances, new_distances)
        
        # On récupère l'index du candidat avec la plus grande distance minimale
        best_idx = np.argmax(min_distances)
        
        # On ajoute le meilleur candidat aux couleurs choisies en récupérant sa sous-matrice associée
        couleurs_choisies = np.vstack([couleurs_choisies, candidats_disponibles[best_idx:best_idx+1]])
        
        # On retire la couleur choisie des couleurs candidats possibles
        candidats_disponibles = np.delete(candidats_disponibles, best_idx, axis=0)

        # On retire également la couleur choisie des distances car on aura 0 à chaque fois après sur son index...
        min_distances = np.delete(min_distances, best_idx)
    
    return couleurs_choisies

def evaluer(selection : RGBArray) -> float:
    """Fonction pour évaluer notre choix de couleurs

    Args:
        selection (RGBArray): Liste de couleurs que l'on souhaite évaluer

    Returns:
        float: retourne la distance minimale entre toutes nos couleurs
    """
    distances = basic_colormath.get_delta_e_matrix(selection, selection)
    np.fill_diagonal(distances, np.inf)
    return np.min(distances)

def generateur_couleur(n : int):
    """Fonction qui permet de générer n couleurs, l'idée est de trouver le nombre chromatique 
    et ensuite d'appeler cette fonction.

    Args:
        n (int): nombre de couleurs que l'on souhaite

    Returns:
        _type_: _description_
    """
    # On génère 10 fois plus de couleurs que nécessaires pour pouvoir maximiser la distance
    candidats = generateur_rgb(10*n) 
    return maximin_delta_e2000(candidats, n)

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
        hex_color = "#%02x%02x%02x" % (int(r), int(g), int(b))

        y0 = 10 + i * (box_height + 5)
        y1 = y0 + box_height

        canvas.create_rectangle(x0, y0, x1, y1, fill=hex_color, outline="black")
        canvas.create_text(350, (y0 + y1) // 2, text=i)

    canvas.configure(scrollregion=canvas.bbox("all"))

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    root.mainloop()

if __name__ =="__main__":
    n = 100 # nombre de couleurs que l'on souhaite obtenir
    liste_couleur = generateur_couleur(n)
    print(f"La liste des couleurs en RGB est :\n {liste_couleur}")
    print(f"La distance minimale parmi cette liste est : {evaluer(liste_couleur)}")
    show_colors(list(liste_couleur))