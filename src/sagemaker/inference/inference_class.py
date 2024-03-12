import os
import json
from datetime import datetime
from fastapi.encoders import jsonable_encoder
import pandas as pd
from joblib import load
from data_models.inference_schema import InferenceSchema
from functools import lru_cache


@lru_cache()
class PredictionService(object):
    std_scaler_model, kmeans_model, xgboost_classifier, name_cat_map = None, None, None, None

    @classmethod
    def load_model_fn(cls, model_dir=os.environ.get("MODEL_DIR")):
        # Load your trained model from the model_dir
        if cls.std_scaler_model is None:
            cls.std_scaler_model = load(f"{model_dir}/std_scaler_model.pkl")
        if cls.kmeans_model is None:
            cls.kmeans_model = load(f"{model_dir}/kmeans_model.pkl")
        if cls.xgboost_classifier is None:
            cls.xgboost_classifier = load(f"{model_dir}/classification_model.pkl")
        if cls.name_cat_map is None:
            with open(f"{model_dir}/classification_model_name_codes.json", "r") as f:
                cls.name_cat_map = json.load(f)
        return cls.std_scaler_model, cls.kmeans_model, cls.xgboost_classifier, cls.name_cat_map

    @classmethod
    def predict_fn(cls, input_data: InferenceSchema):

        data = pd.DataFrame(jsonable_encoder([input_data]))

        # Perform prediction using the model
        std_scaler_model, kmeans_model, xgboost_classifier, name_cat_map = cls.load_model_fn()

        scaled_features = std_scaler_model.transform(data[["usage_freq", "amount_spend", "uniq_merchant"]])
        predicted_cluster = int(kmeans_model.predict([scaled_features[0]])[0])

        # Supervised Classification
        input_df = pd.DataFrame({
            "encd_name": name_cat_map[input_data.name],
            "month": datetime.today().month,
            "weekday": datetime.today().weekday(),
            "k_interval": input_data.k
        }, index=[0]).astype('float64')

        bool_spend_in_k_days = int(xgboost_classifier.predict(input_df)[0])

        return {
            "predicted_cluster": predicted_cluster,
            "will_spend": True if bool_spend_in_k_days==0 else False
        }
