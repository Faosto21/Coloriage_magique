def distance_couleurs(couleur1, couleur2):
    if couleur1 == couleur2:
        return 100
    else:
        return abs(couleur2 - couleur1)