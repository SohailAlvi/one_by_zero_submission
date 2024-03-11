import os
from datetime import datetime
from fastapi.encoders import jsonable_encoder
import pandas as pd
from joblib import load
from data_models.inference_schema import InferenceSchema
from functools import lru_cache


@lru_cache()
class PredictionService(object):
    std_scaler_model, kmeans_model, xgboost_classifier = None, None, None

    @classmethod
    def load_model_fn(cls, model_dir=os.environ.get("MODEL_DIR")):
        # Load your trained model from the model_dir
        if cls.std_scaler_model is None:
            cls.std_scaler_model = load(f"{model_dir}/std_scaler_model.pkl")
        if cls.kmeans_model is None:
            cls.kmeans_model = load(f"{model_dir}/kmeans_model.pkl")
        if cls.xgboost_classifier is None:
            cls.xgboost_classifier = load(f"{model_dir}/classification_model.pkl")
        return cls.std_scaler_model, cls.kmeans_model, cls.xgboost_classifier

    @classmethod
    def predict_fn(cls, input_data: InferenceSchema):

        data = pd.DataFrame(jsonable_encoder([input_data]))

        # Perform prediction using the model
        std_scaler_model, kmeans_model, xgboost_classifier = cls.load_model_fn()

        scaled_features = std_scaler_model.transform(data[["usage_freq", "amount_spend", "uniq_merchant"]])
        predicted_cluster = int(kmeans_model.predict([scaled_features[0]])[0])

        data["transaction_date"] = datetime.today()
        data["weekday"] = data["transaction_date"].dt.weekday
        data["month"] = data["transaction_date"].dt.month

        feature_cols = ["amount_spend", "weekday", "month", "k"]

        bool_spend_in_k_days = int(xgboost_classifier.predict(data[feature_cols].iloc[[0]])[0])

        return {
            "predicted_cluster": predicted_cluster,
            "bool_spend_in_k_days": bool_spend_in_k_days
        }

