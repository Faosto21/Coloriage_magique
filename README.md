# Coloriage_magique
Projet de coloriage magique - M2 Projet professionalisant
Package Python permettant de générer une fenetre Tkinter affichant un calendrier d'opérations de machines qui seront coloriées grâce à l'algorithme de notre choix (DSATUR ou Welsh-Powell). Il suffit de lancer le main pour tester les fonctionnalités et le projet délivré. Le projet est organisé en plusieurs packages et modules.

Quelques chiffres obtenus lors de l'exécution du projet :
Pour 10000 opérations : 
La génération de couleur a mis 0.5755877494812012 secondes
Le partitionnage de DSATUR a mis 19.263306856155396 secondes
L'algorithme a mis 20.030162811279297seconds
Le nombre chromatique est 331
Le coloriage est : {(np.float64(148.8086547605105), np.float64(218.19094005411608), np.float64(149.54579787213947)): {'OF00000044', 'AF00000010'}, (np.float64(212.14674105046478), np.float64(35.41602421001959), np.float64(228.2926301422213)): {'AF00000210', 'OF00000006'}, (np.float64(227.17631230180007), np.float64(127.99826808488615), np.float64(68.51061565705135))
........}

Pour 50000 opérations :
La génération de couleur a mis 0.4266185760498047 secondes
Le partitionnage de DSATUR a mis 290.26592087745667 secondes
L'algorithme a mis 290.9372396469116seconds
Le nombre chromatique est 270

Comparaison de 2 algorithmes pour créer les fichiers planification modifiée et machine modifiée : 
Fichier source : ressources\Planification.txt
Temps base  (10 exécutions) : 197.0049 secondes
Temps gene2 (10 exécutions) : 200.5622 secondes
Rapport : 1.02x plus lent (identique quoi lol)