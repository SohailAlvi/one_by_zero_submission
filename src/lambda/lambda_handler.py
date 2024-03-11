import boto3
import json
import os

SAGEMAKER_ENDPOINT_NAME = os.environ["SAGEMAKER_ENDPOINT_NAME"]
sagemaker_rt_client = boto3.client("sagemaker-runtime", region_name='us-east-1')


def lambda_handler(event, context):
    try:

        body = json.loads(event['body'])

        print(f"Body: {body}")

        data = body.get('input', {})

        if len(data) == 0:
            raise Exception("'input' key missing in the body")

        print(f"Making API with data: {data}")

        api_response = sagemaker_rt_client.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT_NAME,
            ContentType="application/json",
            Body=json.dumps(data)
        )

        api_response = json.loads(api_response['Body'].read().decode('utf-8'))["response"]

        print(f"API Response: {api_response}")

        # Prepare the response
        response = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Received data successfully",
                "response": api_response
            })
        }

        return response
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Exception Occurred",
                "result": str(e)
            })
        }