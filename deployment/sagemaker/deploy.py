import os
from dotenv import load_dotenv
from sagemaker.model import Model

load_dotenv()

# Specify your model artifacts and inference image
inference_image = os.environ.get("INFERENCE_DOCKER_IMAGE")
sagemaker_model_name = os.environ.get("SAGEMAKER_MODEL_NAME")
role_arn = os.environ.get("ROLE_ARN")
instance_type = os.environ.get("INSTANCE_TYPE")

# Create a SageMaker model
sagemaker_model = Model(image_uri=inference_image,
                        role=role_arn)

# Deploy the model as an endpoint
predictor = sagemaker_model.deploy(instance_type=instance_type, initial_instance_count=1)

print(1)