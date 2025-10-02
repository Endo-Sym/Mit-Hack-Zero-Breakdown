"""
ML Predictor wrapper for pm_model_fullpipeline.py
Real-time prediction using trained models
"""
import os
import sys
import joblib
import numpy as np
import pandas as pd

# Add predictive-maintenance to path
PRED_DIR = os.path.join(os.path.dirname(__file__), '..', 'predictive-maintenance')
sys.path.insert(0, PRED_DIR)

class MLPredictor:
    def __init__(self, artifacts_dir="artifacts"):
        """Initialize with trained models"""
        self.artifacts_path = os.path.join(PRED_DIR, artifacts_dir)
        self.models_loaded = False
        self.load_models()

    def load_models(self):
        """Load trained models from artifacts"""
        try:
            # Meta model
            meta_path = os.path.join(self.artifacts_path, 'meta_model.pkl')
            if os.path.exists(meta_path):
                self.meta_model = joblib.load(meta_path)
                self.models_loaded = True
                print(f"✓ Meta model loaded from {meta_path}")

            # Base models (fold 0)
            self.models = {}
            for model_type in ['xgb', 'lgb', 'rf']:
                model_path = os.path.join(self.artifacts_path, f'{model_type}_fold0.pkl')
                scaler_path = os.path.join(self.artifacts_path, f'{model_type}_scaler_fold0.pkl')

                if os.path.exists(model_path):
                    self.models[model_type] = joblib.load(model_path)
                    if os.path.exists(scaler_path):
                        self.models[f'{model_type}_scaler'] = joblib.load(scaler_path)
                    print(f"✓ {model_type} model loaded")

            # Isolation Forest
            iso_path = os.path.join(self.artifacts_path, 'isolationforest_model.pkl')
            if os.path.exists(iso_path):
                self.isolation_forest = joblib.load(iso_path)
                print(f"✓ IsolationForest loaded")

        except Exception as e:
            print(f"⚠ Models not loaded: {str(e)}")
            self.models_loaded = False

    def predict_single(self, sensor_data):
        """
        Predict from single sensor reading

        Args:
            sensor_data: dict with sensor values
                {
                    'PowerMotor': 300,
                    'CurrentMotor': 290,
                    'SpeedMotor': 1485,
                    'TempBrassBearingDE': 65,
                    'TempOilGear': 58,
                    'Vibration': 1.5,
                    ...
                }

        Returns:
            dict with prediction results
        """
        if not self.models_loaded:
            return self.fallback_prediction(sensor_data)

        try:
            # Prepare features
            df = self.prepare_features(sensor_data)
            X = df.values

            # Get base model predictions
            base_preds = []
            for model_type in ['xgb', 'lgb', 'rf']:
                if model_type in self.models:
                    model = self.models[model_type]
                    scaler = self.models.get(f'{model_type}_scaler')

                    X_scaled = scaler.transform(X) if scaler else X
                    pred_proba = model.predict_proba(X_scaled)[:, 1][0]
                    base_preds.append(pred_proba)

            # Stack predictions
            if hasattr(self, 'meta_model') and len(base_preds) >= 3:
                stacked_input = np.array([base_preds])
                risk_probability = self.meta_model.predict_proba(stacked_input)[:, 1][0]
            else:
                risk_probability = np.mean(base_preds) if base_preds else 0.5

            # Anomaly detection
            anomaly_flag = 0
            anomaly_score = 0.0
            if hasattr(self, 'isolation_forest'):
                anomaly_flag = int(self.isolation_forest.predict(X)[0] == -1)
                anomaly_score = float(-self.isolation_forest.decision_function(X)[0])

            # Calculate risk score
            risk_score = int(risk_probability * 100)

            # Risk classification
            if risk_score >= 70:
                risk_level = "สูง"
                prediction = "เครื่องจักรมีความเสี่ยงสูงที่จะเสียหายภายใน 7 วัน ควรหยุดตรวจสอบทันที"
            elif risk_score >= 40:
                risk_level = "ปานกลาง"
                prediction = "เครื่องจักรมีความเสี่ยงปานกลาง ควรติดตามอย่างใกล้ชิดและวางแผนซ่อมบำรุง"
            else:
                risk_level = "ต่ำ"
                prediction = "เครื่องจักรทำงานปกติ มีความเสี่ยงต่ำ"

            # Generate alerts
            alerts = self.generate_alerts(sensor_data, anomaly_flag)

            return {
                "risk_score": risk_score,
                "risk_probability": float(risk_probability),
                "risk_level": risk_level,
                "prediction": prediction,
                "anomaly_flag": anomaly_flag,
                "anomaly_score": float(anomaly_score),
                "alerts": alerts,
                "model_type": "ML Stacked Ensemble (pm_model_fullpipeline)",
                "base_predictions": {
                    "xgb": float(base_preds[0]) if len(base_preds) > 0 else None,
                    "lgb": float(base_preds[1]) if len(base_preds) > 1 else None,
                    "rf": float(base_preds[2]) if len(base_preds) > 2 else None
                }
            }

        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return self.fallback_prediction(sensor_data)

    def prepare_features(self, sensor_data):
        """Prepare features from sensor data"""
        df = pd.DataFrame([sensor_data])

        # Add rolling features (simplified)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols:
            mean_val = df[col].mean()
            std_val = df[col].std() if df[col].std() > 0 else 1
            df[f'{col}_rollmean_3'] = mean_val
            df[f'{col}_rollstd_3'] = std_val
            df[f'{col}_delta_3'] = 0  # No historical data for single prediction

        return df.fillna(0)

    def generate_alerts(self, sensor_data, anomaly_flag=0):
        """Generate alerts based on thresholds"""
        alerts = []
        thresholds = {
            'PowerMotor': {'min': 290, 'max': 315},
            'CurrentMotor': {'min': 280, 'max': 320},
            'TempBrassBearingDE': {'max': 75},
            'TempOilGear': {'max': 65},
            'SpeedMotor': {'min': 1470, 'max': 1500},
            'Vibration': {'max': 1.8},
            'TempWindingMotorPhase_U': {'max': 105},
            'TempWindingMotorPhase_V': {'max': 105},
            'TempWindingMotorPhase_W': {'max': 105}
        }

        for sensor, thresh in thresholds.items():
            if sensor in sensor_data:
                value = sensor_data[sensor]
                if 'min' in thresh and value < thresh['min']:
                    alerts.append(f"{sensor} ต่ำกว่าค่าปกติ: {value}")
                if 'max' in thresh and value > thresh['max']:
                    alerts.append(f"{sensor} สูงกว่าค่าปกติ: {value}")

        if anomaly_flag == 1:
            alerts.append("⚠️ ตรวจพบความผิดปกติจาก ML Anomaly Detection")

        return alerts

    def fallback_prediction(self, sensor_data):
        """Rule-based prediction when ML not available"""
        risk_score = 0
        alerts = []

        power = sensor_data.get('PowerMotor', 300)
        current = sensor_data.get('CurrentMotor', 300)
        temp = sensor_data.get('TempBrassBearingDE', 70)
        vibration = sensor_data.get('Vibration', 1.0)

        if power < 260 or power > 330:
            risk_score += 30
            alerts.append(f"PowerMotor อยู่ในระดับเสี่ยง: {power} kW")
        if current < 240 or current > 360:
            risk_score += 30
            alerts.append(f"CurrentMotor อยู่ในระดับเสี่ยง: {current} Amp")
        if temp > 95:
            risk_score += 25
            alerts.append(f"TempBrassBearingDE สูงเกินไป: {temp}°C")
        if vibration > 4.5:
            risk_score += 30
            alerts.append(f"Vibration อยู่ในระดับอันตราย: {vibration} mm/s")

        risk_level = "สูง" if risk_score >= 60 else "ปานกลาง" if risk_score >= 30 else "ต่ำ"
        prediction = "เครื่องจักรทำงานปกติ" if risk_score < 30 else "ต้องการตรวจสอบ"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "prediction": prediction,
            "alerts": alerts,
            "model_type": "Rule-Based (ML models not loaded)"
        }


# Singleton
_predictor = None

def get_predictor():
    """Get ML predictor singleton"""
    global _predictor
    if _predictor is None:
        _predictor = MLPredictor()
    return _predictor