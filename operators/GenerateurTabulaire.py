from pathlib import Path
import pandas as pd
from datetime import datetime


def generateur_tabulaire(chemin_data: Path, chemin_machines: Path):
    data = pd.read_csv(chemin_data, dtype=str, sep=";")
    data["dtedeb"] = pd.to_datetime(data["dtedeb"])
    data["dtefin"] = pd.to_datetime(data["dtefin"])
    machines = pd.read_csv(chemin_machines, sep=";")
    new_data_path = chemin_data.parent / "Planification_modifiee.txt"
    new_machine_path = chemin_machines.parent / "Machine_modifie.txt"

    for machine, operations in data.groupby("centre"):
        groups = {}
        operations = operations.sort_values("dtedeb")
        for i in range(len(operations)):
            overlap = True
            op1 = operations.iloc[i]
            for num, group in groups.items():
                if group:
                    op2 = group[-1]
                    if not (
                        op2["dtefin"] > op1["dtedeb"]
                    ):  # On vérifie si deux opérations de la même machine se superposent
                        overlap = False
                        break
            if overlap:
                groups[len(groups.keys())] = [op1]
        for num, group in groups.items():
            indice = machines[machines["centre"] == machine].index[0]
            if num == 0:
                continue
            for operation in group:
                operation["centre"] = f"{operation['centre']}_{num}"
                new_row = machines.loc[indice].copy()
                new_row["centre"] = f"{machine}_{num}"
                machines = pd.concat(
                    [
                        machines.iloc[: indice + num],
                        pd.DataFrame([new_row]),
                        machines.iloc[indice + num :],
                    ],
                    ignore_index=True,
                )

    data.to_csv(new_data_path, index=False)
    machines.to_csv(new_machine_path, index=False)


if __name__ == "__main__":
    generateur_tabulaire(
        Path("ressources/Planification.txt"), Path("ressources/Machine.txt")
    )
