# src/geoglows_download.py
# Descarga pronósticos actuales de caudales desde GeoGLOWS para el COMID 620883808  
# Obtiene predicciones a 15 días con intervalos de confianza para análisis operativo

import io
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE = Path("data/raw/geoglows")
BASE.mkdir(parents=True, exist_ok=True)

def download_direct_forecast(comid, nombre):
    """Descarga pronósticos directos desde API v2 con marca temporal para trazabilidad"""
    url = f"https://geoglows.ecmwf.int/api/v2/forecast/{comid}"
    today = datetime.now().strftime("%Y%m%d")
    resp = requests.get(url, headers={"accept": "text/csv"}, timeout=60)
    if resp.status_code == 200 and resp.content:
        df = pd.read_csv(io.StringIO(resp.content.decode("utf-8")))
        out = BASE / f"{nombre}_forecast_direct_{today}.csv"
        df.to_csv(out, index=False)
        print(f"[{nombre}] forecast descargado (directo) -> {out.name}")
    else:
        print(f"⚠️ {nombre} fallo al descargar directo, estado HTTP: {resp.status_code}")

if __name__ == "__main__":
    segmentos = [
        ("rio_620883808", 620883808)
    ]

    for nombre, comid in segmentos:
        download_direct_forecast(comid, nombre)
