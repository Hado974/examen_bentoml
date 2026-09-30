import os
import bentoml
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def train_and_save_model(
    processed_dir: str = "data/processed",
    model_name: str = "admission_lr",
) -> None:
    print("Chargement des donnees traitees...")
    X_train = pd.read_csv(os.path.join(processed_dir, "X_train.csv"))
    y_train = pd.read_csv(os.path.join(processed_dir, "y_train.csv")).values.ravel()
    X_test = pd.read_csv(os.path.join(processed_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(processed_dir, "y_test.csv")).values.ravel()

    print(f"X_train : {X_train.shape}, y_train : {y_train.shape}")
    print(f"X_test  : {X_test.shape}, y_test  : {y_test.shape}")

    # Initialisation et entrainement du modele de regression lineaire
    print("Entrainement du modele LinearRegression...")
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Evaluation des performances sur le jeu de test
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)

    print("\n================ Performances du Modele ================")
    print(f"R2 Score : {r2:.4f}")
    print(f"MAE      : {mae:.4f}")
    print(f"RMSE     : {rmse:.4f}")
    print("========================================================\n")

    # Sauvegarde du modele dans le Model Store de BentoML
    print(f"Sauvegarde du modele '{model_name}' dans le Model Store BentoML...")
    saved_model = bentoml.sklearn.save_model(
        model_name,
        model,
        signatures={
            "predict": {"batchable": True, "batch_dim": 0},
        },
        metadata={
            "r2_score": float(r2),
            "mae": float(mae),
            "rmse": float(rmse),
            "feature_names": list(X_train.columns),
        },
    )
    print(f"Modele sauvegarde avec succes : {saved_model.tag}")


if __name__ == "__main__":
    train_and_save_model()
