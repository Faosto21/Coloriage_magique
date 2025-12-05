import numpy as np
import basic_colormath

from typing import Annotated
from numpy.typing import NDArray

RGBArray = Annotated[
    NDArray[np.float64],
    "Shape: (n, 3), Range: [0, 255]"
]

def generateur_rgb(
        n: int
        ) -> RGBArray:
    """Génère n couleurs RGB"""

    # On génère n couleurs en HSL pour avoir des couleurs optimales
    hues = np.linspace(0, 365, n, endpoint=False) % 365 # Uniformité en teinte sur le disque
    saturation = np.random.uniform(20, 80, n) # Saturation pour pastel
    lightness = np.random.uniform(50, 75, n) # Luminosité moyenne pour éviter blanc/noir
    hsl_colors = np.column_stack([hues, saturation, lightness])
 
    return basic_colormath.hsls_to_rgb(hsl_colors)

def maximin_delta_e2000(
        candidats: RGBArray, 
        n: int
        ) -> RGBArray:
    """Sélectionne n couleurs maximisant la distance Delta E 2000"""
    
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

def evaluer(selection):
    distances = basic_colormath.get_delta_e_matrix(selection, selection)
    np.fill_diagonal(distances, np.inf)
    return np.min(distances)

def generateur_couleur(n : int):
    candidats = generateur_rgb(10*n)
    return maximin_delta_e2000(candidats, n)

if __name__ =="__main__":
    n = 50 # nombre de couleurs
    liste_couleur = generateur_couleur(n)
    print(liste_couleur)
    print(evaluer(liste_couleur))