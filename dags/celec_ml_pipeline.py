# dags/celec_ml_pipeline.py
# Airflow DAG for CELEC Flow Prediction ML Pipeline
# Este workflow orquesta el pipeline completo de ML sin modificar los scripts existentes

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.utils.dates import days_ago
import os

# Configuración por defecto del DAG
default_args = {
    'owner': 'celec-data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

# Definir el DAG
dag = DAG(
    'celec_flow_prediction_pipeline',
    default_args=default_args,
    description='Complete CELEC ML Pipeline with MLflow tracking',
    schedule_interval='0 6 * * *',  # Ejecutar diariamente a las 6 AM
    tags=['ml', 'hydrology', 'celec', 'production'],
    max_active_runs=1,  # Solo un pipeline activo a la vez
)

def check_environment():
    """Verifica que el ambiente virtual y dependencias estén activos"""
    import sys
    import subprocess
    
    print("🔍 Verificando ambiente Python...")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Verificar MLflow
    try:
        import mlflow
        print(f"✅ MLflow version: {mlflow.__version__}")
    except ImportError:
        raise Exception("❌ MLflow no está instalado")
    
    # Verificar scikit-learn
    try:
        import sklearn
        print(f"✅ Scikit-learn version: {sklearn.__version__}")
    except ImportError:
        raise Exception("❌ Scikit-learn no está instalado")
    
    print("✅ Ambiente verificado correctamente")

def validate_data():
    """Valida que los datos estén disponibles y sean válidos"""
    import pandas as pd
    from pathlib import Path
    
    print("🔍 Validando datos de entrada...")
    
    data_file = Path("data/raw/620883808_retrospective_data.csv")
    if not data_file.exists():
        raise Exception(f"❌ Archivo de datos no encontrado: {data_file}")
    
    # Cargar y validar datos
    df = pd.read_csv(data_file)
    print(f"📊 Datos cargados: {len(df)} registros")
    
    # Validaciones básicas
    if len(df) < 1000:
        raise Exception(f"❌ Insuficientes registros de datos: {len(df)}")
    
    if df.isnull().sum().sum() > len(df) * 0.1:  # Más del 10% nulos
        print("⚠️ Advertencia: Alto porcentaje de valores faltantes")
    
    print("✅ Datos validados correctamente")

def notify_completion(**context):
    """Notifica la finalización del pipeline"""
    task_instance = context['task_instance']
    dag_run = context['dag_run']
    
    print("🎉 Pipeline CELEC completado exitosamente!")
    print(f"DAG Run ID: {dag_run.run_id}")
    print(f"Execution Date: {dag_run.execution_date}")
    
    # Aquí podrías añadir notificaciones a Slack, Teams, etc.
    return "Pipeline completed successfully"

# ===== DEFINIR TAREAS =====

# 1. Verificar ambiente
check_env_task = PythonOperator(
    task_id='check_environment',
    python_callable=check_environment,
    dag=dag,
)

# 2. Validar datos de entrada
validate_data_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)

# 3. Descargar datos actualizados (si es necesario)
download_data_task = BashOperator(
    task_id='download_retrospective_data',
    bash_command='''
    cd {{ params.project_dir }}
    echo "🔄 Descargando datos retrospectivos..."
    python src/data/download_retrospective.py
    echo "✅ Datos descargados exitosamente"
    ''',
    params={'project_dir': '/c/Users/david/Downloads/CELEC_forecast-develop'},
    dag=dag,
)

# 4. Ejecutar modelo básico (preservando funcionalidad existente)
run_basic_model_task = BashOperator(
    task_id='run_basic_model',
    bash_command='''
    cd {{ params.project_dir }}
    echo "🤖 Ejecutando modelo básico..."
    python src/models/data_analysis.py
    echo "✅ Modelo básico completado"
    ''',
    params={'project_dir': '/c/Users/david/Downloads/CELEC_forecast-develop'},
    dag=dag,
)

# 5. Ejecutar modelo con MLflow (script existente sin modificar)
run_mlflow_model_task = BashOperator(
    task_id='run_mlflow_model',
    bash_command='''
    cd {{ params.project_dir }}
    echo "🔬 Ejecutando modelo con MLflow tracking completo..."
    python run_with_mlflow.py
    echo "✅ Modelo MLflow completado"
    ''',
    params={'project_dir': '/c/Users/david/Downloads/CELEC_forecast-develop'},
    dag=dag,
)

# 6. Validar resultados del modelo
validate_results_task = BashOperator(
    task_id='validate_model_results',
    bash_command='''
    cd {{ params.project_dir }}
    echo "🔍 Validando resultados del modelo..."
    
    # Verificar que los archivos de salida existen
    if [ -f "data/processed/model_predictions.csv" ]; then
        echo "✅ Predicciones generadas correctamente"
    else
        echo "❌ Error: No se generaron predicciones"
        exit 1
    fi
    
    if [ -f "data/processed/feature_importance.csv" ]; then
        echo "✅ Feature importance generada correctamente"
    else
        echo "⚠️ Advertencia: Feature importance no encontrada"
    fi
    
    if [ -f "models/trained_model.pkl" ]; then
        echo "✅ Modelo guardado correctamente"
    else
        echo "❌ Error: Modelo no fue guardado"
        exit 1
    fi
    
    echo "✅ Validación de resultados completada"
    ''',
    params={'project_dir': '/c/Users/david/Downloads/CELEC_forecast-develop'},
    dag=dag,
)

# 7. Generar reporte de pipeline
generate_report_task = BashOperator(
    task_id='generate_pipeline_report',
    bash_command='''
    cd {{ params.project_dir }}
    echo "📊 Generando reporte del pipeline..."
    
    # Crear reporte básico
    echo "CELEC ML Pipeline Report - $(date)" > reports/pipeline_report.txt
    echo "=================================" >> reports/pipeline_report.txt
    echo "" >> reports/pipeline_report.txt
    
    if [ -f "data/processed/model_predictions.csv" ]; then
        echo "✅ Modelo ejecutado exitosamente" >> reports/pipeline_report.txt
        echo "📊 Predicciones generadas: $(wc -l < data/processed/model_predictions.csv) registros" >> reports/pipeline_report.txt
    fi
    
    if [ -f "models/trained_model.pkl" ]; then
        echo "💾 Modelo guardado: models/trained_model.pkl" >> reports/pipeline_report.txt
    fi
    
    echo "" >> reports/pipeline_report.txt
    echo "🕒 Pipeline completado: $(date)" >> reports/pipeline_report.txt
    
    echo "✅ Reporte generado en reports/pipeline_report.txt"
    ''',
    params={'project_dir': '/c/Users/david/Downloads/CELEC_forecast-develop'},
    dag=dag,
)

# 8. Notificación final
notify_completion_task = PythonOperator(
    task_id='notify_completion',
    python_callable=notify_completion,
    dag=dag,
)

# ===== DEFINIR DEPENDENCIAS =====
check_env_task >> validate_data_task >> download_data_task
download_data_task >> run_basic_model_task >> run_mlflow_model_task
run_mlflow_model_task >> validate_results_task >> generate_report_task
generate_report_task >> notify_completion_task

# Configuración de alertas por email (opcional)
email_on_failure = EmailOperator(
    task_id='send_email_on_failure',
    to=['admin@celec.gov.ec'],
    subject='🚨 CELEC ML Pipeline Failed',
    html_content='''
    <h3>CELEC Flow Prediction Pipeline Failed</h3>
    <p>El pipeline de ML de CELEC ha fallado en la ejecución.</p>
    <p>DAG: {{ dag.dag_id }}</p>
    <p>Execution Time: {{ ds }}</p>
    <p>Por favor revisar los logs en Airflow UI.</p>
    ''',
    dag=dag,
    trigger_rule='one_failed',  # Solo se ejecuta si alguna tarea falla
)

# Conectar email de fallo a todas las tareas críticas
for task in [run_basic_model_task, run_mlflow_model_task, validate_results_task]:
    task >> email_on_failure