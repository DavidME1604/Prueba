# src/download_retrospective.py  
# Descarga datos históricos desde la API de GeoGLOWS para el COMID 620883808
# Obtiene serie temporal completa 1940-2025 para entrenamiento del modelo predictivo

import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("data/raw")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def download_retrospective_data(comid, nombre):
    """Descarga datos retrospectivos diarios desde endpoint v2 de GeoGLOWS"""
    print(f"Descargando datos retrospectivos para {nombre} (COMID: {comid})...")
    
    # URL de GeoGLOWS para datos retrospectivos
    url = f"https://geoglows.ecmwf.int/api/v2/retrospective/{comid}"
    
    try:
        response = requests.get(url, headers={"accept": "text/csv"}, timeout=120)
        
        if response.status_code == 200 and response.content:
            # Leer datos
            df = pd.read_csv(pd.io.common.StringIO(response.text))
            
            # Guardar archivo
            filename = f"{comid}_retrospective_data.csv"
            output_path = BASE_DIR / filename
            df.to_csv(output_path, index=False)
            
            print(f"Datos guardados en: {output_path}")
            print(f"Registros descargados: {len(df)}")
            
            # Mostrar info básica
            if len(df.columns) >= 2:
                time_col = df.columns[0]
                flow_col = df.columns[1] 
                print(f"Período: {df[time_col].min()} a {df[time_col].max()}")
                print(f"Caudal promedio: {df[flow_col].mean():.2f} m³/s")
                print(f"Rango: {df[flow_col].min():.2f} - {df[flow_col].max():.2f} m³/s")
            
            return True
            
        else:
            print(f"Error al descargar. Código HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error durante la descarga: {e}")
        return False

if __name__ == "__main__":
    # Descargar para COMID 620883808
    comid = 620883808
    nombre = "rio_620883808"
    
    success = download_retrospective_data(comid, nombre)
    
    if success:
        print(f"\nDescarga completada exitosamente!")
    else:
        print(f"\nFalló la descarga")