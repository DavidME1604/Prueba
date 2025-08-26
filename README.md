# Electricity Demand Forecast for Ecuador 🇪🇨

Forecasting Ecuador's electricity demand using machine learning for CELEC..

## 📈 Project Overview
This project applies state-of-the-art ML models to predict electricity demand across Ecuador, supporting CELEC in resource planning and grid operations.

## 📁 Repository Structure
- `data/raw/` - Datos históricos y pronósticos de GeoGLOWS
- `data/processed/` - Resultados del modelo y predicciones  
- `src/` - Scripts principales del proyecto
- `notebooks/` - Análisis exploratorio (EDA)
- `reports/figures/` - Gráficos y visualizaciones
- `mlruns/` - Experimentos MLflow

## 🚀 Quick Start

### **Prerequisites**
- **Python 3.11+** (recommended for full MLflow compatibility)
- **Git** for version control
- **Virtual environment** (recommended)

### **Step 1: Environment Setup**
```bash
# Clone repository
git clone https://github.com/carol230/CELEC_forecast.git
cd CELEC_forecast

# Create virtual environment
python -m venv celec_env

# Activate virtual environment
# Windows:
celec_env\Scripts\activate
# macOS/Linux:
source celec_env/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### **Step 2: Data Download**
```bash
# Download historical data (1940-2025)
python src/data/download_retrospective.py
```

### **Step 3: Model Training (Choose One)**

#### **Option A: Basic Model**
```bash
# Run basic Random Forest model
python src/models/data_analysis.py
```

#### **Option B: Full MLflow Tracking**
```bash
# Run model with full MLflow experiment tracking
python run_with_mlflow.py

# Start MLflow UI dashboard
python start_mlflow_ui.py
# Open browser: http://127.0.0.1:5000
```

### **Using Make Commands (Optional)**
```bash
# Install dependencies
make requirements

# Download data and train model
make train

# Run MLflow experiment
make mlflow

# Start MLflow UI
make mlflow-ui
```

## 🎯 **Scripts Principales**

### **Core Scripts:**
- **`src/models/data_analysis.py`** - Modelo Random Forest básico (R² = 0.984)
- **`src/data/download_retrospective.py`** - Descarga datos históricos (1940-2025)
- **`src/data/geoglows_download.py`** - Descarga pronósticos actuales GeoGLOWS

### **MLflow Scripts (Python 3.11):**
- **`run_with_mlflow.py`** - Modelo con tracking MLflow completo
- **`start_mlflow_ui.py`** - Inicia dashboard web MLflow

## 🔬 **MLflow Dashboard**

**Con Python 3.11 tienes acceso a:**
- 📊 Dashboard interactivo en `http://127.0.0.1:5000`
- 📈 Comparación de experimentos y métricas
- 📁 Descarga de modelos y artifacts
- 🏷️ Modelo registrado: `CELEC_Flow_Predictor`
- 📊 Métricas: MAE, RMSE, R², gráficos interactivos

## 📊 **Resultados Generados**

- `data/processed/model_predictions.csv` - Predicciones del modelo
- `models/trained_model.pkl` - Modelo entrenado básico
- `reports/figures/*.png` - Gráficos de análisis
- `mlruns/` - Experimentos MLflow completos

## 📊 Model Results

**Modelo Random Forest para COMID 620883808:**
- **R² Score**: 0.984 (98.4% precisión)
- **MAE**: 0.60 m³/s 
- **RMSE**: 1.56 m³/s
- **Datos**: 85 años (1940-2025), 31,248 registros
- **División**: 70% entrenamiento, 30% prueba temporal

## 📝 License
MIT License

## 🧹 **Limpieza de Archivos**

**Archivos que se pueden eliminar:**
- `.claude/settings.local.json` (ya eliminado)
- `data/processed/experiment_summary.json` (ya eliminado)
- `mlruns/534430952526196641/` (experimento obsoleto)
- `src/mlflow_advanced.py` (ya eliminado)
- `mlruns/.trash/` (archivos de basura)

## 📁 **Project Structure (Cookiecutter Data Science)**

```
CELEC_forecast/
├── data/
│   ├── external/               # Data from third party sources
│   ├── interim/                # Intermediate data that has been transformed
│   ├── processed/              # The final, canonical data sets for modeling
│   └── raw/                    # The original, immutable data dump
├── docs/                       # A default Sphinx project; see sphinx-doc.org for details
├── models/                     # Trained and serialized models, model predictions
├── notebooks/                  # Jupyter notebooks (01-pg-exploratory-data-analysis.ipynb)
├── references/                 # Data dictionaries, manuals, and all other materials
├── reports/                    # Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures/                # Generated graphics and figures
├── requirements.txt            # pip requirements file
├── src/                        # Source code for use in this project
│   ├── __init__.py            # Makes src a Python module
│   ├── data/                   # Scripts to download or generate data
│   │   ├── __init__.py
│   │   ├── download_retrospective.py
│   │   └── geoglows_download.py
│   ├── features/               # Scripts to turn raw data into features for modeling
│   │   └── __init__.py
│   ├── models/                 # Scripts to train models and then use trained models to make predictions
│   │   ├── __init__.py
│   │   └── data_analysis.py
│   └── visualization/          # Scripts to create exploratory and results oriented visualizations
│       └── __init__.py
├── Makefile                    # Makefile with commands like `make data` or `make train`
├── mlruns/                     # MLflow experiments and artifacts
├── run_with_mlflow.py          # MLflow experiment runner
├── start_mlflow_ui.py          # MLflow UI server
└── test_environment.py         # Test python environment setup
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **Import Error: No module named 'mlflow'**
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

#### **FileNotFoundError: data/raw/620883808_retrospective_data.csv**
```bash
# Solution: Download data first
python src/data/download_retrospective.py
```

#### **MLflow UI not starting**
```bash
# Check if MLflow is installed
pip show mlflow

# Start with explicit port
mlflow ui --port 5000
```

#### **Python version issues**
```bash
# Check Python version
python --version

# Use Python 3.11+ for full compatibility
```

### **Quick Setup Script**
```bash
# Automated setup (Windows/Linux/macOS)
python setup.py
```

### **Verification Commands**
```bash
# Test environment
python test_environment.py

# Verify all dependencies
pip list

# Check if data exists
ls data/raw/
```

## 🧪 Testing

```bash
# Run basic model test
python src/models/data_analysis.py

# Verify model output
ls models/
ls data/processed/
ls reports/figures/
```

## 📚 Dependencies

All dependencies are specified in `requirements.txt`:
- **Core ML**: pandas, numpy, scikit-learn
- **Visualization**: matplotlib, seaborn, plotly
- **MLflow**: experiment tracking and model registry
- **Utils**: joblib, requests, pathlib

## 🙋‍♂️ Contact

