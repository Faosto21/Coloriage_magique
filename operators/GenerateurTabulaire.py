from pathlib import Path
import pandas as pd


def generateur_tabulaire(chemin_data: Path, chemin_machines: Path):
    data = pd.read_csv(chemin_data, dtype=str, sep=";")
    data["dtedeb"] = pd.to_datetime(data["dtedeb"])
    data["dtefin"] = pd.to_datetime(data["dtefin"])
    machines = pd.read_csv(chemin_machines, sep=";")
    new_data_path = chemin_data.parent / "Planification_modifiee.txt"
    new_machine_path = chemin_machines.parent / "Machine_modifie.txt"

    for machine, operations in data.groupby("centre"):
        ops = operations.sort_values("dtedeb")
        groups = {}  # idx : liste des indices des opérations
        # On bosse avec les indices pour simplifier les accès et écriture avec Pandas
        for idx, ope in ops.iterrows():
            placed = False
            # On cherche un groupe (liste d'opérations) où la dernière opération se termine avant le début de l'opération actuel
            for num, group in groups.items():
                dernier_idx = group[-1]
                fin_precedente = data.loc[dernier_idx, "dtefin"]
                debut_suivant = ope["dtedeb"]
                if (
                    fin_precedente <= debut_suivant
                ):  # On vérifie qu'il n'y a pas de chevauchement
                    group.append(idx)  # On ajoute l'INDEX au groupe
                    placed = True
                    break
            # Si chevauchement sur toutes les autres operations on crée un nouveau groupe
            if not placed:
                groups[len(groups)] = [idx]
        # Pour chaque groupe (ligne) supplémentaire, on va créer une nouvelle machine et mettre à jour les opérations
        indice = machines[machines["centre"] == machine].index[0]
        # On parcourt les groupes dans l'ordre pour ordonner les numéros de machine
        for num in sorted(groups.keys()):
            if num == 0:
                continue
            # Crée une nouvelle ligne machine par groupe (num)
            new_row = machines.loc[indice].copy()
            new_row["centre"] = f"{machine}_{num}"
            # On l'insère après la dernière "sous-machine" de la même machine
            machines = pd.concat(
                [
                    machines.iloc[: indice + num],
                    pd.DataFrame([new_row]),
                    machines.iloc[indice + num :],
                ],
                ignore_index=True,
            )
            # Met à jour les opérations pour ce groupe pour Planification.txt
            for operation_idx in groups[num]:
                data.loc[operation_idx, "centre"] = f"{machine}_{num}"

    # On retransforme en .txt
    data.to_csv(new_data_path, index=False, sep=";")
    machines.to_csv(new_machine_path, index=False)


if __name__ == "__main__":
    generateur_tabulaire(
        Path("ressources/Planification.txt"), Path("ressources/Machine.txt")
    )
