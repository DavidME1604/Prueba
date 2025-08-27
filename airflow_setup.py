#!/usr/bin/env python3
# airflow_setup.py
# Script de configuración automática para Airflow con el proyecto CELEC
# Este script prepara el ambiente sin afectar la funcionalidad existente

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description, capture_output=False):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=capture_output, text=True)
        if capture_output:
            return result.stdout
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}:")
        if capture_output and e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_docker():
    """Verifica que Docker esté instalado y funcionando"""
    print("🐳 Verificando Docker...")
    
    # Verificar docker command
    if not run_command("docker --version", "Verificar Docker", capture_output=True):
        print("❌ Docker no está instalado o no está en el PATH")
        print("   Por favor instalar Docker Desktop: https://www.docker.com/products/docker-desktop")
        return False
    
    # Verificar docker-compose
    if not run_command("docker-compose --version", "Verificar Docker Compose", capture_output=True):
        print("❌ Docker Compose no está disponible")
        return False
    
    # Verificar que Docker esté corriendo
    if not run_command("docker ps", "Verificar Docker daemon", capture_output=True):
        print("❌ Docker daemon no está corriendo")
        print("   Por favor iniciar Docker Desktop")
        return False
    
    print("✅ Docker está configurado correctamente")
    return True

def setup_airflow_directories():
    """Crea directorios necesarios para Airflow"""
    print("📁 Configurando directorios de Airflow...")
    
    directories = [
        "dags",
        "logs", 
        "config",
        "plugins",
        "reports"  # Asegurar que existe para el pipeline
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   📂 {directory}/")
    
    print("✅ Directorios configurados")

def create_env_file():
    """Crea archivo .env para configuración de Airflow"""
    print("⚙️ Creando configuración de ambiente...")
    
    # Determinar UID apropiado
    if platform.system() != "Windows":
        try:
            airflow_uid = os.getuid()
        except:
            airflow_uid = 50000
    else:
        airflow_uid = 50000
    
    env_content = f"""# Configuración de Airflow para CELEC
AIRFLOW_UID={airflow_uid}
AIRFLOW_PROJ_DIR=.

# Usuarios de Airflow
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=celec123

# Variables del proyecto CELEC
CELEC_PROJECT_DIR=/opt/airflow/celec_project
CELEC_MODEL_NAME=CELEC_Flow_Predictor
CELEC_COMID=620883808

# MLflow
MLFLOW_TRACKING_URI=http://mlflow-server:5000
"""
    
    with open(".env.airflow", "w") as f:
        f.write(env_content)
    
    print("✅ Archivo .env.airflow creado")

def create_startup_script():
    """Crea script de inicio fácil para Airflow"""
    print("🚀 Creando scripts de inicio...")
    
    # Script para Windows
    windows_script = """@echo off
echo 🚀 Iniciando Airflow para proyecto CELEC...
echo.
echo Dashboard estará disponible en:
echo   - Airflow UI: http://localhost:8080 (admin/celec123)
echo   - MLflow UI: http://localhost:5000
echo.

REM Asegurar que Docker esté corriendo
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está corriendo. Por favor iniciar Docker Desktop.
    pause
    exit /b 1
)

REM Inicializar Airflow
echo 📦 Inicializando servicios...
docker-compose -f docker-compose.airflow.yml --env-file .env.airflow up airflow-init

REM Iniciar servicios
echo 🔄 Iniciando servicios de Airflow...
docker-compose -f docker-compose.airflow.yml --env-file .env.airflow up -d

echo.
echo ✅ Airflow iniciado exitosamente!
echo 📊 Abrir dashboard: http://localhost:8080
echo 🔬 MLflow disponible en: http://localhost:5000
echo.
echo Para detener: stop_airflow.bat
pause
"""
    
    with open("start_airflow.bat", "w") as f:
        f.write(windows_script)
    
    # Script de parada para Windows
    stop_script = """@echo off
echo 🛑 Deteniendo servicios de Airflow...
docker-compose -f docker-compose.airflow.yml --env-file .env.airflow down
echo ✅ Servicios detenidos
pause
"""
    
    with open("stop_airflow.bat", "w") as f:
        f.write(stop_script)
    
    # Scripts para Unix/Linux
    unix_start_script = """#!/bin/bash
echo "🚀 Iniciando Airflow para proyecto CELEC..."
echo
echo "Dashboard estará disponible en:"
echo "  - Airflow UI: http://localhost:8080 (admin/celec123)"  
echo "  - MLflow UI: http://localhost:5000"
echo

# Verificar Docker
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor iniciar Docker."
    exit 1
fi

# Inicializar Airflow
echo "📦 Inicializando servicios..."
docker-compose -f docker-compose.airflow.yml --env-file .env.airflow up airflow-init

# Iniciar servicios
echo "🔄 Iniciando servicios de Airflow..."
docker-compose -f docker-compose.airflow.yml --env-file .env.airflow up -d

echo
echo "✅ Airflow iniciado exitosamente!"
echo "📊 Abrir dashboard: http://localhost:8080"
echo "🔬 MLflow disponible en: http://localhost:5000"
echo
echo "Para detener: ./stop_airflow.sh"
"""
    
    with open("start_airflow.sh", "w") as f:
        f.write(unix_start_script)
    
    unix_stop_script = """#!/bin/bash
echo "🛑 Deteniendo servicios de Airflow..."
docker-compose -f docker-compose.airflow.yml --env-file .env.airflow down
echo "✅ Servicios detenidos"
"""
    
    with open("stop_airflow.sh", "w") as f:
        f.write(unix_stop_script)
    
    # Hacer ejecutables en Unix
    if platform.system() != "Windows":
        os.chmod("start_airflow.sh", 0o755)
        os.chmod("stop_airflow.sh", 0o755)
    
    print("✅ Scripts de inicio creados")

def update_gitignore():
    """Actualiza .gitignore para excluir archivos de Airflow"""
    print("📝 Actualizando .gitignore...")
    
    gitignore_additions = """
# Airflow
logs/
.env.airflow
airflow.cfg
webserver_config.py

# Docker volumes
postgres-db-volume/
"""
    
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            current_content = f.read()
        
        if "# Airflow" not in current_content:
            with open(gitignore_path, "a") as f:
                f.write(gitignore_additions)
            print("✅ .gitignore actualizado")
        else:
            print("✅ .gitignore ya contiene configuración de Airflow")
    else:
        print("⚠️ .gitignore no encontrado, omitiendo actualización")

def main():
    """Función principal de configuración"""
    print("🌊 CELEC Airflow Setup")
    print("=" * 50)
    print("Este script configura Apache Airflow para orquestar")
    print("el pipeline de ML sin modificar scripts existentes.")
    print()
    
    # Verificar que estamos en el directorio correcto
    if not Path("run_with_mlflow.py").exists():
        print("❌ Error: Este script debe ejecutarse desde el directorio raíz del proyecto CELEC")
        print("   Directorio actual:", os.getcwd())
        sys.exit(1)
    
    print("📍 Directorio del proyecto:", os.getcwd())
    print()
    
    # Verificaciones y configuración
    if not check_docker():
        print("\n❌ Configuración de Docker requerida antes de continuar")
        sys.exit(1)
    
    setup_airflow_directories()
    create_env_file()
    create_startup_script()
    update_gitignore()
    
    print("\n" + "=" * 60)
    print("🎉 ¡CONFIGURACIÓN DE AIRFLOW COMPLETADA!")
    print("=" * 60)
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Iniciar Airflow:")
    if platform.system() == "Windows":
        print("   → Ejecutar: start_airflow.bat")
    else:
        print("   → Ejecutar: ./start_airflow.sh")
    
    print("\n2. Abrir dashboards:")
    print("   → Airflow UI: http://localhost:8080")
    print("     Usuario: admin | Contraseña: celec123")
    print("   → MLflow UI: http://localhost:5000")
    
    print("\n3. Activar DAG:")
    print("   → En Airflow UI, buscar 'celec_flow_prediction_pipeline'")
    print("   → Activar el toggle del DAG")
    print("   → Ejecutar manualmente o esperar programación")
    
    print("\n4. Detener servicios cuando termines:")
    if platform.system() == "Windows":
        print("   → Ejecutar: stop_airflow.bat")
    else:
        print("   → Ejecutar: ./stop_airflow.sh")
    
    print("\n💡 NOTA IMPORTANTE:")
    print("   Todos los scripts existentes siguen funcionando independientemente.")
    print("   Airflow es una capa adicional de orquestación.")
    print("\n✅ Setup completado exitosamente!")

if __name__ == "__main__":
    main()