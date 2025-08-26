# src/data_analysis.py
# Modelo predictivo de caudales basado en datos retrospectivos de GeoGLOWS
# Implementa Random Forest con ingeniería de características para predecir caudales del COMID 620883808
# División temporal 70/30 para entrenamiento y validación del modelo

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
import mlflow
import joblib
warnings.filterwarnings('ignore')

# Configuración de paths
RAW_DIR = Path("data/raw")
PROC_DIR = Path("data/processed")  
MODELS_DIR = Path("models")
FIG_DIR = Path("reports/figures")
PROC_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

def load_retrospective_data():
    """Carga y prepara datos retrospectivos del COMID 620883808 desde archivo CSV"""
    print("Cargando datos retrospectivos...")
    df = pd.read_csv(RAW_DIR / "620883808_retrospective_data.csv")
    df['time'] = pd.to_datetime(df['time'])
    df = df.rename(columns={'620883808': 'caudal'})
    df = df.sort_values('time').reset_index(drop=True)
    print(f"Cargados {len(df)} registros desde {df['time'].min()} hasta {df['time'].max()}")
    return df

def create_features(df):
    """Genera características temporales, lags y ventanas móviles para el modelo ML"""
    print("Creando features...")
    
    # Features temporales
    df['year'] = df['time'].dt.year
    df['month'] = df['time'].dt.month
    df['day'] = df['time'].dt.day
    df['dayofyear'] = df['time'].dt.dayofyear
    df['quarter'] = df['time'].dt.quarter
    
    # Features estacionales (componentes cíclicas)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['day_sin'] = np.sin(2 * np.pi * df['dayofyear'] / 365)
    df['day_cos'] = np.cos(2 * np.pi * df['dayofyear'] / 365)
    
    # Features de lags (valores anteriores)
    for lag in [1, 2, 3, 7, 15, 30]:
        df[f'caudal_lag_{lag}'] = df['caudal'].shift(lag)
    
    # Features de ventanas móviles
    for window in [3, 7, 15, 30]:
        df[f'caudal_rolling_mean_{window}'] = df['caudal'].rolling(window=window).mean()
        df[f'caudal_rolling_std_{window}'] = df['caudal'].rolling(window=window).std()
    
    # Eliminar filas con NaN
    df = df.dropna().reset_index(drop=True)
    print(f"Features creadas. Datos finales: {len(df)} registros")
    return df

def train_test_split_temporal(df, test_size=0.3):
    """Realiza división temporal cronológica para validación realista del modelo"""
    split_date = df['time'].quantile(1 - test_size)
    
    train_df = df[df['time'] < split_date].copy()
    test_df = df[df['time'] >= split_date].copy()
    
    print(f"División temporal:")
    print(f"  Entrenamiento: {train_df['time'].min()} a {train_df['time'].max()} ({len(train_df)} registros)")
    print(f"  Prueba: {test_df['time'].min()} a {test_df['time'].max()} ({len(test_df)} registros)")
    
    return train_df, test_df

def prepare_ml_data(df):
    """Prepara datos para ML (separa features de target)"""
    feature_cols = [col for col in df.columns if col not in ['time', 'caudal']]
    X = df[feature_cols]
    y = df['caudal']
    return X, y, feature_cols

def train_model(X_train, y_train):
    """Entrena modelo Random Forest optimizado para predicción de series temporales"""
    print("Entrenando modelo Random Forest...")
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    print("Modelo entrenado")
    return model

def evaluate_model(model, X_test, y_test, feature_names):
    """Evalúa rendimiento del modelo y analiza importancia de características"""
    print("Evaluando modelo...")
    
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Métricas del modelo:")
    print(f"  MAE: {mae:.2f} m³/s")
    print(f"  RMSE: {rmse:.2f} m³/s") 
    print(f"  R²: {r2:.3f}")
    
    # Feature importance
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop 10 features más importantes:")
    for i, (_, row) in enumerate(importance_df.head(10).iterrows()):
        print(f"  {i+1:2d}. {row['feature']:<25} {row['importance']:.3f}")
    
    return y_pred, importance_df

def save_results(test_df, y_pred, importance_df):
    """Guarda resultados"""
    print("Guardando resultados...")
    
    # Predicciones vs reales
    results_df = test_df[['time', 'caudal']].copy()
    results_df['caudal_pred'] = y_pred
    results_df['error'] = results_df['caudal'] - results_df['caudal_pred']
    results_df['error_abs'] = np.abs(results_df['error'])
    results_df['error_pct'] = (results_df['error'] / results_df['caudal']) * 100
    
    results_df.to_csv(PROC_DIR / "model_predictions.csv", index=False)
    importance_df.to_csv(PROC_DIR / "feature_importance.csv", index=False)
    
    print("Resultados guardados en data/processed/")
    return results_df

def create_plots(results_df, importance_df):
    """Crea gráficos de resultados"""
    print("Creando gráficos...")
    
    # 1. Predicciones vs Reales (serie temporal)
    plt.figure(figsize=(15, 6))
    plt.plot(results_df['time'], results_df['caudal'], label='Real', alpha=0.7)
    plt.plot(results_df['time'], results_df['caudal_pred'], label='Predicho', alpha=0.8)
    plt.title('Predicción vs Realidad - Caudales COMID 620883808')
    plt.xlabel('Fecha')
    plt.ylabel('Caudal (m³/s)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "model_predictions_timeseries.png", dpi=300)
    plt.close()
    
    # 2. Scatter plot predicciones vs reales
    plt.figure(figsize=(8, 8))
    plt.scatter(results_df['caudal'], results_df['caudal_pred'], alpha=0.5)
    min_val = min(results_df['caudal'].min(), results_df['caudal_pred'].min())
    max_val = max(results_df['caudal'].max(), results_df['caudal_pred'].max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
    plt.xlabel('Caudal Real (m³/s)')
    plt.ylabel('Caudal Predicho (m³/s)')
    plt.title('Predicciones vs Valores Reales')
    plt.tight_layout()
    plt.savefig(FIG_DIR / "model_predictions_scatter.png", dpi=300)
    plt.close()
    
    # 3. Feature importance
    plt.figure(figsize=(10, 8))
    top_15 = importance_df.head(15)
    plt.barh(range(len(top_15)), top_15['importance'])
    plt.yticks(range(len(top_15)), top_15['feature'])
    plt.xlabel('Importancia')
    plt.title('Top 15 Features más Importantes')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "feature_importance.png", dpi=300)
    plt.close()
    
    # 4. Distribución de errores
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.hist(results_df['error'], bins=50, alpha=0.7, edgecolor='black')
    plt.xlabel('Error (m³/s)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de Errores')
    
    plt.subplot(1, 2, 2)
    plt.hist(results_df['error_pct'], bins=50, alpha=0.7, edgecolor='black')
    plt.xlabel('Error (%)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de Errores Porcentuales')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / "error_distribution.png", dpi=300)
    plt.close()
    
    print("Gráficos guardados en reports/figures/")

def main():
    """Ejecuta el pipeline completo de entrenamiento y evaluación del modelo predictivo"""
    print("Iniciando análisis y entrenamiento del modelo predictivo de caudales")
    print("=" * 70)
    
    # 1. Cargar datos
    df = load_retrospective_data()
    
    # 2. Crear features
    df = create_features(df)
    
    # 3. División temporal 70/30
    train_df, test_df = train_test_split_temporal(df, test_size=0.3)
    
    # 4. Preparar datos para ML
    X_train, y_train, feature_names = prepare_ml_data(train_df)
    X_test, y_test, _ = prepare_ml_data(test_df)
    
    # 5. Entrenar modelo
    model = train_model(X_train, y_train)
    
    # 6. Evaluar modelo
    y_pred, importance_df = evaluate_model(model, X_test, y_test, feature_names)
    
    # 7. Guardar resultados
    results_df = save_results(test_df, y_pred, importance_df)
    
    # 8. Crear gráficos
    create_plots(results_df, importance_df)
    
    # 9. Guardar modelo
    model_path = MODELS_DIR / "trained_model.pkl"
    joblib.dump(model, model_path)
    print(f"Modelo guardado en: {model_path}")
    
    # 10. Registrar métricas finales
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\nMétricas finales registradas:")
    print(f"  MAE: {mae:.2f} m³/s")
    print(f"  RMSE: {rmse:.2f} m³/s")
    print(f"  R²: {r2:.3f}")
    
    print("=" * 70)
    print("Análisis completado! Revisa los resultados en:")
    print("   data/processed/ - Datos procesados")  
    print("   reports/figures/ - Gráficos")
    
    return model, results_df, importance_df

if __name__ == "__main__":
    model, results, importance = main()