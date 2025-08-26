# MLflow Integration Guide - CELEC Forecast

## 📋 Overview
This guide explains how to use MLflow for experiment tracking and model management in the CELEC hydrological forecasting project.

## 🔧 Setup Requirements

### Python 3.11 Environment
MLflow UI requires Python 3.11 for full functionality:
```bash
# Activate virtual environment
celec_mlflow_env\Scripts\Activate.ps1
```

### Basic Model (Python 3.13)
For basic model without MLflow UI:
```bash
python src/data_analysis.py
```

## 🚀 Running MLflow Experiments

### 1. Execute Model with MLflow Tracking
```bash
python run_with_mlflow.py
```

### 2. Start MLflow UI Dashboard
```bash
python start_mlflow_ui.py
# Access: http://127.0.0.1:5000
```

## 📊 MLflow Components

### Experiments Tracked
- **Experiment Name**: `CELEC_Flow_Prediction_Full`
- **Model Registry**: `CELEC_Flow_Predictor`

### Logged Parameters
- `data_records`: Total number of data points
- `data_start_date` / `data_end_date`: Data time range
- `features_created`: Number of engineered features
- `train_size` / `test_size`: Dataset split sizes
- `model_type`: RandomForest
- Hyperparameters: `n_estimators`, `max_depth`, etc.

### Logged Metrics
- `mae`: Mean Absolute Error
- `mse`: Mean Squared Error  
- `rmse`: Root Mean Squared Error
- `r2_score`: Coefficient of Determination

### Logged Artifacts
- `random_forest_model/`: Complete model artifacts
- `model_predictions.csv`: Test predictions
- `feature_importance.csv`: Feature importance scores
- `*.png`: All visualization plots

### Tags
- `comid`: Stream identifier (620883808)
- `model_purpose`: hydrological_forecast
- `data_source`: geoglows_retrospective
- `python_version`: 3.11

## 🎯 Model Registry

The trained model is automatically registered as `CELEC_Flow_Predictor` and can be:
- Downloaded for production use
- Versioned for model lifecycle management
- Compared across different runs

## 📁 File Structure
```
mlruns/
├── 0/                          # Default experiment
├── 615754683786599151/         # CELEC experiment ID
│   └── [run_id]/
│       ├── artifacts/          # Model and plots
│       ├── metrics/            # Metric values
│       ├── params/             # Parameters
│       └── tags/               # Run tags
└── models/
    └── CELEC_Flow_Predictor/   # Registered model
```

## 🔍 Using the MLflow UI

1. **Experiments Tab**: Compare runs, metrics, and parameters
2. **Models Tab**: Manage registered models and versions
3. **Artifacts**: Download models and visualizations
4. **Plots**: Interactive metric comparisons

## 💡 Best Practices

1. Always run experiments in the Python 3.11 environment
2. Use descriptive run names and tags
3. Log all relevant parameters and metrics
4. Store artifacts for reproducibility
5. Use model registry for version control

## 🛠️ Troubleshooting

- **MLflow UI not starting**: Ensure Python 3.11 environment is active
- **Missing artifacts**: Check file paths in `run_with_mlflow.py`
- **Port conflicts**: MLflow UI uses port 5000 by default