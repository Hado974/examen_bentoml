import os
import pandas as pd
from sklearn.model_selection import train_test_split


def prepare_data(
    input_path: str = "data/raw/admission.csv",
    output_dir: str = "data/processed",
    test_size: float = 0.2,
    random_state: int = 42,
) -> None:
    print(f"Chargement des donnees depuis {input_path}...")
    df = pd.read_csv(input_path)

    # Nettoyage des noms de colonnes (suppression des espaces superflus)
    df.columns = df.columns.str.strip()

    # Suppression de la colonne d'identifiant 'Serial No.' (inutile a la prediction)
    if "Serial No." in df.columns:
        df = df.drop(columns=["Serial No."])

    # Verification de la variable cible
    target_col = "Chance of Admit"
    if target_col not in df.columns:
        raise ValueError(f"Colonne cible '{target_col}' absente du dataset.")

    # Separation des variables explicatives (X) et de la cible (y)
    X = df.drop(columns=[target_col])
    y = df[target_col]

    print(f"Dimensions initiales : {df.shape}")
    print(f"Variables explicatives : {list(X.columns)}")

    # Decoupage en jeu d'entrainement et de test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Creation du dossier de destination si necessaire
    os.makedirs(output_dir, exist_ok=True)

    # Sauvegarde des fichiers dans data/processed/
    X_train.to_csv(os.path.join(output_dir, "X_train.csv"), index=False)
    X_test.to_csv(os.path.join(output_dir, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(output_dir, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(output_dir, "y_test.csv"), index=False)

    print(f"Donnees traitees sauvegardees avec succes dans {output_dir}/")
    print(f"X_train : {X_train.shape}, X_test : {X_test.shape}")
    print(f"y_train : {y_train.shape}, y_test : {y_test.shape}")


if __name__ == "__main__":
    prepare_data()
