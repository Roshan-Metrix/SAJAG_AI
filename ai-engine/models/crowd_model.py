"""
CrowdDensityModel – classifies crowd density level and predicts stampede risk.
Uses XGBClassifier (density level) and XGBRegressor (stampede risk).
"""

import numpy as np
import pandas as pd
from pathlib import Path

from config import MODELS_DIR

try:
    import joblib
except ImportError:  # pragma: no cover – expected in minimal envs
    joblib = None

try:
    from xgboost import XGBClassifier, XGBRegressor
except ImportError:  # pragma: no cover
    XGBClassifier = None
    XGBRegressor = None

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, f1_score


# ── Feature list – must match columns produced by generate_crowd_dataset ──────
CROWD_FEATURES = [
    "hour_of_day", "day_of_week", "month", "event_type",
    "venue_capacity", "estimated_crowd", "area_m2",
    "entry_points", "emergency_exits", "security_personnel",
    "ambient_temp_c", "occupancy_ratio", "density_per_m2",
]

DENSITY_LABELS = {
    0: "NORMAL",
    1: "DENSE",
    2: "OVERCROWDED",
    3: "CRITICAL",
}

MODEL_PATH = MODELS_DIR / "crowd_model.pkl"


# ── Static helpers ────────────────────────────────────────────────────────────

def _risk_level(risk: float) -> str:
    if risk >= 0.80:
        return "CRITICAL"
    if risk >= 0.60:
        return "HIGH"
    if risk >= 0.35:
        return "MEDIUM"
    return "LOW"


def _action(density_level: int, stampede_risk: float) -> str:
    if density_level >= 3 or stampede_risk >= 0.80:
        return "EVACUATE_IMMEDIATE"
    if density_level == 2 or stampede_risk >= 0.60:
        return "RESTRICT_ENTRY"
    if density_level == 1 or stampede_risk >= 0.35:
        return "MONITOR_SITUATION"
    return "NORMAL_OPERATIONS"


def _generate_alerts(density_level: int, stampede_risk: float, features: dict) -> list:
    alerts = []
    occ = features.get("occupancy_ratio", 0.0)
    density = features.get("density_per_m2", 0.0)
    entry_points = features.get("entry_points", 0)
    exits = features.get("emergency_exits", 0)

    if density_level >= 3:
        alerts.append("CRITICAL: Venue at maximum capacity. Initiate crowd control.")
    if stampede_risk >= 0.80:
        alerts.append("ALERT: Stampede risk CRITICAL. Evacuate in order.")
    if occ > 0.90:
        alerts.append(f"WARNING: Occupancy at {occ:.0%}. Risk of crush.")
    if density > 3.0:
        alerts.append(f"DANGER: Density {density:.2f} pers/m2 exceeds safe limit.")
    if entry_points < 3:
        alerts.append("CAUTION: Limited entry points – bottleneck risk.")
    if exits < 4:
        alerts.append("CAUTION: Limited emergency exits – evacuation hazard.")
    if stampede_risk >= 0.60:
        alerts.append("WARN: High stampede risk. Deploy security personnel.")
    return alerts


# ── Model class ───────────────────────────────────────────────────────────────

class CrowdDensityModel:
    """
    Two-model ensemble:
      - XGBClassifier  → crowd_density_level  (0–3)
      - XGBRegressor   → stampede_risk         (0–1 continuous)
    """

    def __init__(self):
        if XGBClassifier is None or XGBRegressor is None:
            raise ImportError("xgboost is required for CrowdDensityModel")

        self.clf = XGBClassifier(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1,
        )
        self.reg = XGBRegressor(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.feature_importances_: dict = {}
        self.is_trained = False

    # ── Feature engineering ──────────────────────────────────────────────────

    @staticmethod
    def _engineer_features(X: pd.DataFrame) -> pd.DataFrame:
        """Add derived columns; returns a new DataFrame."""
        X = X.copy()
        # crowding pressure: crowd vs. capacity
        X["crowd_capacity_ratio"] = (
            X["estimated_crowd"] / X["venue_capacity"].clip(lower=1)
        )
        # congestion: entries/exits
        X["entry_exit_ratio"] = (
            X["entry_points"] / X["emergency_exits"].clip(lower=1)
        )
        # temporal risk (night events higher risk)
        X["is_night_event"] = ((X["hour_of_day"] >= 22) | (X["hour_of_day"] <= 5)).astype(int)
        # rush hour proxy
        X["is_rush_hour"] = (
            ((X["hour_of_day"] >= 7) & (X["hour_of_day"] <= 9)) |
            ((X["hour_of_day"] >= 17) & (X["hour_of_day"] <= 19))
        ).astype(int)
        return X

    # ── Train ────────────────────────────────────────────────────────────────

    def train(self, df: pd.DataFrame) -> dict:
        X = df[CROWD_FEATURES].copy()
        y_cls = df["crowd_density_level"]
        y_reg = df["stampede_risk"]

        X = self._engineer_features(X)
        X_scaled = self.scaler.fit_transform(X)

        X_train, X_test, y_cls_train, y_cls_test, _, y_reg_test = train_test_split(
            X_scaled, y_cls, y_reg,
            test_size=0.2,
            stratify=y_cls,
            random_state=42,
        )
        # Re-split y_reg to match
        _, _, _, _, y_reg_train, _ = train_test_split(
            X_scaled, y_cls, y_reg,
            test_size=0.2,
            stratify=y_cls,
            random_state=42,
        )

        self.clf.fit(X_train, y_cls_train)
        self.reg.fit(X_train, y_reg_train)

        # Feature importances
        self.feature_importances_ = {
            col: float(v)
            for col, v in zip(X.columns, self.clf.feature_importances_)
        }

        # Metrics
        reg_pred = self.reg.predict(X_test)
        stampede_rmse = float(np.sqrt(mean_squared_error(y_reg_test, reg_pred)))
        stampede_r2   = float(r2_score(y_reg_test, reg_pred))

        cls_pred = self.clf.predict(X_test)
        density_f1 = float(f1_score(y_cls_test, cls_pred, average="weighted"))

        self.is_trained = True

        return {
            "stampede_rmse": stampede_rmse,
            "stampede_r2": stampede_r2,
            "density_f1": density_f1,
            "feature_importances": self.feature_importances_,
        }

    # ── Predict ──────────────────────────────────────────────────────────────

    def predict(self, features: dict) -> dict:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions.")

        row = pd.DataFrame([features])[CROWD_FEATURES]
        row = self._engineer_features(row)
        row_sc = self.scaler.transform(row)

        cls_proba = self.clf.predict_proba(row_sc)[0]
        cls_pred  = int(np.argmax(cls_proba))
        stamp_risk = float(np.clip(self.reg.predict(row_sc)[0], 0.0, 1.0))

        return {
            "density_level": cls_pred,
            "density_label": DENSITY_LABELS[cls_pred],
            "stampede_risk": round(stamp_risk, 4),
            "stampede_risk_level": _risk_level(stamp_risk),
            "class_probabilities": {
                DENSITY_LABELS[i]: round(float(p), 4)
                for i, p in enumerate(cls_proba)
            },
            "recommended_action": _action(cls_pred, stamp_risk),
            "alerts": _generate_alerts(cls_pred, stamp_risk, features),
        }

    # ── Save / Load ──────────────────────────────────────────────────────────

    def save(self, path: Path | str | None = None) -> Path:
        if joblib is None:
            raise ImportError("joblib is required to save/load the model.")
        path = Path(path) if path else MODEL_PATH
        payload = {
            "clf": self.clf,
            "reg": self.reg,
            "scaler": self.scaler,
            "feature_importances": self.feature_importances_,
            "is_trained": self.is_trained,
        }
        joblib.dump(payload, path)
        return path

    @classmethod
    def load(cls, path: Path | str | None = None) -> "CrowdDensityModel":
        if joblib is None:
            raise ImportError("joblib is required to save/load the model.")
        path = Path(path) if path else MODEL_PATH
        payload = joblib.load(path)
        model = cls()
        model.clf = payload["clf"]
        model.reg = payload["reg"]
        model.scaler = payload["scaler"]
        model.feature_importances_ = payload["feature_importances"]
        model.is_trained = payload["is_trained"]
        return model