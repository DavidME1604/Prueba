# start_mlflow_ui.py
# Script para iniciar MLflow UI con la configuración correcta
# Requiere ambiente virtual Python 3.11: celec_mlflow_env\Scripts\Activate.ps1

import subprocess
import sys
import os

def start_mlflow_ui():
    """Inicia MLflow UI con la configuración del proyecto CELEC"""
    
    print("Iniciando MLflow UI para proyecto CELEC...")
    print("Dashboard disponible en: http://127.0.0.1:5000")
    print("Presiona Ctrl+C para detener el servidor")
    print("-" * 50)
    
    try:
        # Iniciar MLflow UI
        subprocess.run([
            "mlflow", "ui", 
            "--port", "5000",
            "--backend-store-uri", "file:./mlruns"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\nServidor MLflow detenido.")
    except subprocess.CalledProcessError as e:
        print(f"Error iniciando MLflow UI: {e}")
        print("Asegúrate de estar en el ambiente virtual correcto:")
        print("celec_mlflow_env\\Scripts\\Activate.ps1")

if __name__ == "__main__":
    start_mlflow_ui()