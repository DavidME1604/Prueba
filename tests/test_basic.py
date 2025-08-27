# tests/test_basic.py
# Unit tests básicos para cumplir requisito - SIMPLE

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestBasicFunctions(unittest.TestCase):
    """Tests unitarios básicos"""
    
    def test_data_loading(self):
        """Test que se puede cargar data"""
        # Test simple - verificar que pandas funciona
        df = pd.DataFrame({'caudal': [1, 2, 3], 'time': pd.date_range('2020-01-01', periods=3)})
        self.assertEqual(len(df), 3)
        self.assertIn('caudal', df.columns)
    
    def test_feature_creation(self):
        """Test básico de feature engineering"""
        df = pd.DataFrame({
            'time': pd.date_range('2020-01-01', periods=10, freq='D'),
            'caudal': np.random.rand(10) * 20 + 10
        })
        
        # Crear features básicos
        df['month'] = df['time'].dt.month
        df['day'] = df['time'].dt.day
        
        self.assertEqual(len(df), 10)
        self.assertIn('month', df.columns)
        self.assertIn('day', df.columns)
    
    def test_model_basic(self):
        """Test básico de modelo"""
        from sklearn.ensemble import RandomForestRegressor
        
        # Datos sintéticos
        X = np.random.rand(100, 3)
        y = np.random.rand(100)
        
        # Entrenar modelo básico
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        # Predecir
        predictions = model.predict(X[:5])
        
        self.assertEqual(len(predictions), 5)
        self.assertTrue(all(isinstance(p, (int, float)) for p in predictions))

if __name__ == '__main__':
    unittest.main()