# 🌊 CELEC Airflow Workflow Guide

Este documento explica cómo utilizar Apache Airflow para orquestar el pipeline completo de ML del proyecto CELEC sin afectar la funcionalidad existente.

## 📋 Qué es Airflow

Apache Airflow es una plataforma de orquestación que permite:
- **Programar** pipelines para ejecutarse automáticamente
- **Monitorear** el estado de cada tarea
- **Gestionar dependencias** entre tareas
- **Reintentar** tareas fallidas automáticamente
- **Paralelizar** tareas independientes

## 🎯 Pipeline CELEC Implementado

El DAG `celec_flow_prediction_pipeline` orquesta las siguientes tareas:

```
1. check_environment       → Verifica Python, MLflow, scikit-learn
2. validate_data           → Valida datos de entrada
3. download_data           → Ejecuta download_retrospective.py
4. run_basic_model         → Ejecuta data_analysis.py (existente)
5. run_mlflow_model        → Ejecuta run_with_mlflow.py (existente)
6. validate_results        → Verifica que se generaron outputs
7. generate_report         → Crea reporte del pipeline
8. notify_completion       → Notifica finalización
```

**⚠️ IMPORTANTE:** Los scripts existentes NO se modifican, solo se ejecutan vía Airflow.

## 🚀 Setup Rápido

### 1. Ejecutar Configuración Automática
```bash
python airflow_setup.py
```

### 2. Iniciar Airflow

**Windows:**
```bash
start_airflow.bat
```

**Linux/Mac:**
```bash
./start_airflow.sh
```

### 3. Acceder a Dashboards

- **Airflow UI:** http://localhost:8080
  - Usuario: `admin`
  - Contraseña: `celec123`

- **MLflow UI:** http://localhost:5000

## 📊 Uso del Dashboard

### Activar el Pipeline
1. Ir a http://localhost:8080
2. Buscar DAG `celec_flow_prediction_pipeline`
3. Activar el toggle (OFF → ON)
4. El pipeline se ejecutará diariamente a las 6 AM

### Ejecutar Manualmente
1. Click en el DAG name
2. Click "Trigger DAG" (botón ▶️)
3. Confirmar ejecución

### Monitorear Progreso
- **Graph View:** Ver dependencias entre tareas
- **Tree View:** Ver ejecuciones históricas
- **Logs:** Click en cualquier tarea para ver logs detallados

## ⚙️ Configuración del Pipeline

### Programación
El pipeline se ejecuta:
- **Frecuencia:** Diaria a las 6:00 AM
- **Zona horaria:** UTC
- **Reintentos:** 2 intentos por tarea fallida
- **Delay entre reintentos:** 5 minutos

### Modificar Programación
En `dags/celec_ml_pipeline.py`, línea 24:
```python
schedule_interval='0 6 * * *',  # Cambiar formato cron
```

Ejemplos:
- `'0 */6 * * *'` - Cada 6 horas
- `'0 0 * * 1'` - Cada lunes
- `None` - Solo ejecución manual

## 🔧 Personalización

### Añadir Tareas
```python
new_task = BashOperator(
    task_id='nueva_tarea',
    bash_command='python mi_script.py',
    dag=dag,
)

# Definir dependencias
existing_task >> new_task >> next_task
```

### Configurar Notificaciones Email
En el DAG, actualizar:
```python
email_on_failure = EmailOperator(
    to=['tu-email@ejemplo.com'],  # Cambiar email
    # ... resto de configuración
)
```

### Variables de Ambiente
Añadir en `.env.airflow`:
```bash
MI_VARIABLE=mi_valor
```

Usar en DAG:
```python
import os
mi_valor = os.getenv('MI_VARIABLE')
```

## 🔍 Troubleshooting

### Pipeline Falla
1. **Ver logs:** Click en tarea fallida → "Log"
2. **Verificar datos:** ¿Existe `data/raw/620883808_retrospective_data.csv`?
3. **Verificar ambiente:** ¿MLflow instalado correctamente?
4. **Reintentar:** Click "Clear" en tarea fallida

### Docker Issues
```bash
# Ver contenedores corriendo
docker ps

# Ver logs de servicio específico
docker-compose -f docker-compose.airflow.yml logs airflow-webserver

# Reiniciar servicios
stop_airflow.bat  # o ./stop_airflow.sh
start_airflow.bat # o ./start_airflow.sh
```

### Permisos (Linux/Mac)
```bash
# Si hay problemas de permisos
sudo chown -R $USER:$USER logs/
chmod 755 start_airflow.sh stop_airflow.sh
```

## 📈 Monitoreo y Métricas

### Dashboard de Estado
- **Success Rate:** Porcentaje de ejecuciones exitosas
- **Duration:** Tiempo promedio de ejecución
- **Last Run:** Estado de la última ejecución

### Integración con MLflow
- Todos los experimentos se registran automáticamente
- Métricas disponibles en http://localhost:5000
- Modelos versionados en el registry

### Logs Centralizados
- Todos los logs en `logs/` directory
- Organizados por DAG, tarea y fecha
- Búsqueda integrada en Airflow UI

## 🔄 Workflows Avanzados

### Pipeline de Re-entrenamiento
```python
# Trigger cuando hay nuevos datos
file_sensor = FileSensor(
    task_id='wait_for_new_data',
    filepath='data/raw/new_data_flag.txt',
    dag=dag,
)

file_sensor >> run_mlflow_model_task
```

### Validación de Modelo
```python
# Comparar con modelo anterior
model_validation_task = PythonOperator(
    task_id='validate_model_performance',
    python_callable=compare_model_metrics,
    dag=dag,
)
```

### Deployment Condicional
```python
# Deploy solo si R2 > 0.95
deploy_task = BashOperator(
    task_id='deploy_model',
    bash_command='python deploy_model.py',
    dag=dag,
    trigger_rule='all_success',  # Solo si todas las tareas previas pasaron
)
```

## 🛑 Detener Servicios

**Windows:**
```bash
stop_airflow.bat
```

**Linux/Mac:**
```bash
./stop_airflow.sh
```

## 📚 Recursos Adicionales

- [Documentación Oficial de Airflow](https://airflow.apache.org/docs/)
- [Tutorial de DAGs](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)
- [Operators Reference](https://airflow.apache.org/docs/apache-airflow/stable/operators-and-hooks-ref/index.html)

## ✅ Verificación de Funcionalidad

Para confirmar que todo funciona correctamente:

1. **Scripts Existentes:** 
   ```bash
   # Estos DEBEN seguir funcionando independientemente
   python src/models/data_analysis.py
   python run_with_mlflow.py
   python start_mlflow_ui.py
   ```

2. **Pipeline de Airflow:**
   ```bash
   # Abrir http://localhost:8080
   # Ejecutar DAG manualmente
   # Verificar que todas las tareas pasen
   ```

3. **Outputs Generados:**
   ```bash
   # Verificar que se crean estos archivos
   ls data/processed/model_predictions.csv
   ls models/trained_model.pkl
   ls reports/figures/*.png
   ```

---

**🔑 Punto Clave:** Airflow es una capa de orquestación que NO modifica el código existente. Todos los scripts originales siguen funcionando exactamente igual, pero ahora también pueden ejecutarse de forma programada y monitoreada través de Airflow.