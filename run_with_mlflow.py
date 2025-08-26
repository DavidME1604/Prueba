# run_with_mlflow.py
# Script principal para ejecutar el modelo CELEC con MLflow UI completo
# Requiere ambiente virtual Python 3.11: celec_mlflow_env\Scripts\Activate.ps1

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# MLflow imports (ahora funcionan con Python 3.11)
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# Importar funciones del modelo principal
from src.models.data_analysis import (
    load_retrospective_data, create_features, train_test_split_temporal,
    prepare_ml_data, train_model, evaluate_model, save_results, create_plots
)

def main_with_full_mlflow():
    """Ejecuta el modelo con MLflow UI completo"""
    
    print("Ejecutando modelo CELEC con MLflow completo")
    print("=" * 60)
    
    # Configurar MLflow
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("CELEC_Flow_Prediction_Full")
    
    with mlflow.start_run() as run:
        print(f"Run ID: {run.info.run_id}")
        
        # 1. Cargar datos
        df = load_retrospective_data()
        mlflow.log_param("data_records", len(df))
        mlflow.log_param("data_start_date", str(df['time'].min()))
        mlflow.log_param("data_end_date", str(df['time'].max()))
        
        # 2. Crear features
        df = create_features(df)
        features_count = len([col for col in df.columns if col not in ['time', 'caudal']])
        mlflow.log_param("features_created", features_count)
        
        # 3. División temporal 70/30
        train_df, test_df = train_test_split_temporal(df, test_size=0.3)
        mlflow.log_param("train_size", len(train_df))
        mlflow.log_param("test_size", len(test_df))
        mlflow.log_param("test_split_ratio", 0.3)
        
        # 4. Preparar datos para ML
        X_train, y_train, feature_names = prepare_ml_data(train_df)
        X_test, y_test, _ = prepare_ml_data(test_df)
        
        # 5. Entrenar modelo
        model = train_model(X_train, y_train)
        
        # Log model parameters
        mlflow.log_param("model_type", "RandomForest")
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("max_depth", 20)
        mlflow.log_param("min_samples_split", 5)
        mlflow.log_param("min_samples_leaf", 2)
        mlflow.log_param("random_state", 42)
        
        # 6. Evaluar modelo
        y_pred, importance_df = evaluate_model(model, X_test, y_test, feature_names)
        
        # Log metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2_score", r2)
        
        # 7. Guardar resultados
        results_df = save_results(test_df, y_pred, importance_df)
        
        # 8. Crear gráficos
        create_plots(results_df, importance_df)
        
        # 9. Log model usando MLflow sklearn
        mlflow.sklearn.log_model(
            model, 
            "random_forest_model",
            registered_model_name="CELEC_Flow_Predictor"
        )
        
        # 10. Log artifacts
        mlflow.log_artifact("data/processed/model_predictions.csv")
        mlflow.log_artifact("data/processed/feature_importance.csv")
        
        # Log all figures
        for fig_file in Path("reports/figures").glob("*.png"):
            mlflow.log_artifact(str(fig_file))
        
        # Log tags
        mlflow.set_tag("comid", "620883808")
        mlflow.set_tag("model_purpose", "hydrological_forecast")
        mlflow.set_tag("data_source", "geoglows_retrospective")
        mlflow.set_tag("python_version", "3.11")
        
        print(f"\nExperimento completado!")
        print(f"   Run ID: {run.info.run_id}")
        print(f"   MAE: {mae:.2f} m/s")
        print(f"   R2: {r2:.3f}")
        
    print("\nPara ver el MLflow UI ejecuta:")
    print("   mlflow ui")
    print("   Luego abre: http://localhost:5000")

if __name__ == "__main__":
    main_with_full_mlflow()