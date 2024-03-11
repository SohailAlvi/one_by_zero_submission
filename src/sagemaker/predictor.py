import logging

from fastapi import FastAPI, responses
from data_models.inference_schema import InferenceSchema
from inference.inference_class import PredictionService


# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)


app = FastAPI()


@app.get("/ping")
async def ping():
    return responses.JSONResponse(content={"status": "ok"}, status_code=200)


@app.post("/invocations")
async def invocation(input_data: InferenceSchema):
    results = PredictionService().predict_fn(input_data)
    return responses.JSONResponse(content={"response": results}, status_code=200)
