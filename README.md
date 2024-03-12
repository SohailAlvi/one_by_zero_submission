# OneByZero Assignment(AWS MLOps)


1) [Description](#des)
2) [Directory Structure](#directory-structure)
3) [Requirements](#requirements)
   1) [AWS Services](#aws-services)
4) [Setup](#setup)
   1) [Docker Image Creation](#docker-image-creation)
   2) [Sagemaker Model Deployment](#sagemaker-model-deployment)
   3) [Lambda Creation](#lambda-creation)
   4) [API Gateway](#api-gateway)
5) [Testing the API](#testing-the-api)
6) [Model Versioning](#model-versioning)
7) [Auto-Scaling and Security](#auto-scaling-and-security)
   1) [Sagemaker Endpoint](#aws-sagemaker-endpoint)
   2) [Lambda Function](#aws-lambda-function)
   3) [API Gateway](#aws-api-gateway)
8) [Data Drift](#data-drift)



## Description

This repository contains code and instructions for deploying a credit card transaction model using AWS services. The project involves training two models: 
1) A clustering model to cluster cardholders based on their transaction behavior
2) And a supervised model to predict if a cardholder will make a purchase in the next k days. 
3) The trained models are then deployed as endpoints in AWS SageMaker, and a REST API is created using AWS Lambda and API Gateway for making predictions.



## Directory Structure

```
one_by_zero_submission/
│
├── data/ # Transactional Data of Credit Card Holders
├── deployment/ # Python and Terraform scripts to deploy Sagemaker Endpoint and Lambda Function
├── models/ # Directory to store trained models
├── notebooks/ # Jupyter / IPython notebooks for data exploration and model building
├── src/ # Source code for model serving and Lambda handler
│ ├── lambda/ # Code for Lambda handler
│ └── sagemaker/ # Code for model serving to be used in Sagemaker endpoint
└── .gitignore
└── Dockerfile # Documentation files
└── requirements.txt # Documentation files
└── README.md # API documentation
```



## Requirements

### AWS Services
- Amazon S3: For storing datasets and trained models.
- SageMaker: For deploying machine learning models.
- Lambda: For serverless computing to run code in response to events.
- API Gateway: For creating, deploying, and managing APIs.


## Setup

### Docker Image creation

- Use notebooks in ./notebooks to load the data and train the clustering and supervised models.
- Build the Docker image from the root directory.
```bash
docker build -t <image_name>:latest .
```
- Push this image to AWS ECR, you must have your credentials configured via **aws** cli .


###  Sagemaker Model Deployment

- For this step **Role_ARN** is required along with above create image **ECR Repository**
-  Run the following commands
```bash
python ./deployment/sagemaker/deploy.py
```
- Withing approximately 5-10 minutes, endpoint will be ready to use.
- Use the following code to test the endpoint:
```python
import boto3
import json

# Create a low-level client representing Amazon SageMaker Runtime
sagemaker_runtime = boto3.client(
    "sagemaker-runtime", region_name='us-east-1')

# The endpoint name must be unique within
# an AWS Region in your AWS account.
endpoint_name="<aws_sagemaker_endpoint_name>"

# Gets inference from the model hosted at the specified endpoint:
response = sagemaker_runtime.invoke_endpoint(
    EndpointName=endpoint_name,
    Body=json.dumps({
    "usage_freq": 4,
    "amount_spend": 490,
    "uniq_merchant": 5,
    "k": 9
    })
    )

# Decodes and prints the response body:
print(response['Body'].read().decode('utf-8'))
```

### Lambda Creation
- Use the following command to create Lambda Execution role
```bash
cd ./deployment/terraform/lambda
# Replace the variables with original values
# Create lambda_function_payload.zip which should consist of ./src/lambda/lambda_handler.py
terraform init
terraform apply
```


### API Gateway
- For this project we created REST API Gateway via **AWS Console**
- And Attached the above created Lambda Function to this Gateway.



## Testing the API
```bash
# This is the actual API deployed in AWS Infra

curl --location 'https://fqdgpmbgc9.execute-api.us-east-1.amazonaws.com/Staging/api-ml-model' \
--header 'Content-Type: application/json' \
--data '{
    "input": {
    
    "usage_freq": 1,
    "amount_spend": 40000,
    "uniq_merchant": 89,
    "k": 6,
    "name": "C_Mason"
    
}
}'
```
Expected response:
```json
{
    "message": "Received data successfully",
    "response": {
        "predicted_cluster": 4,
        "will_spend": true
    }
}
```

## Model Versioning

- For Model Versioning, **MLFlow**'s model registry will be helpful in
tracking model version's as well as their environment.
[Model Registry](https://mlflow.org/docs/latest/model-registry.html)


## Auto-Scaling and Security
Note: All of the services used in this project are managed by AWS

### AWS Sagemaker Endpoint
- Increase number of instances
- Use AWS CloudWatch alarms to trigger auto-scaling. 


### AWS Lambda Function
- AWS Lambda serverless is a managed service which can handle default 1000 concurrent Lambda functions
- For further heavy load, additional concurrency has to be requested from the AWS.


### AWS API Gateway
- Enabling API caching to enhance responsiveness
- Use **AWS Shield** against DDos attacks
- AWS Cognito User Pool for Authorization

### Data drift
- Detection Approaches
  - Drop in accuracy calculated from user feedback.
  - PageHinkley
```python
from river.drift import PageHinkley
import numpy as np

# Generate random data stream
np.random.seed(0)  # For reproducibility
data_stream = np.random.normal(loc=0, scale=50, size=1000)  # Random data stream

# Initialize PageHinkley drift detector
page_hinkley_detector = PageHinkley(delta=0.005, threshold=50)

# Simulate data stream and detect concept drift
for i, data_point in enumerate(data_stream):
    # Update the detector with new data point
    page_hinkley_detector.update(data_point)
    
    # Check if concept drift occurred
    if page_hinkley_detector.change_detected:
        print(f"Change detected at index {i}.")

# After processing the stream, print statistics
print(f"Total number of data points processed: {i + 1}")

```
  - Adaptive Windowing (ADWIN):
``` python
import numpy as np
from skmultiflow.drift_detection import ADWIN

# Generate random data stream
np.random.seed(0)  # For reproducibility
data_stream = np.random.normal(loc=0, scale=1, size=1000)
# Initialize ADWIN detector
adwin_detector = ADWIN()

# Simulate data stream and detect concept drift
for i, data_point in enumerate(data_stream):
    # Update the detector with new data point
    adwin_detector.add_element(data_point)
    
    # Check if concept drift occurred
    if adwin_detector.detected_change():
        print(f"Change detected at index {i}.")

# After processing the stream, print statistics
print(f"Total number of data points: {adwin_detector.total}")
```