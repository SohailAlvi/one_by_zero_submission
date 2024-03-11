provider "aws" {
  region = "us-east-1"
}

resource "aws_lambda_function" "terraform_ml_lambda_function" {
  function_name    = "terraform_ml_lambda_function"
  role             = aws_iam_role.terraform-ml-lambda-execution-role.arn
  handler          = "lambda_handler.lambda_handler"
  runtime          = "python3.8"
  filename         = "lambda_function_payload.zip"
  source_code_hash = filebase64sha256("lambda_function_payload.zip")

  environment {
    variables = {
      SAGEMAKER_ENDPOINT_NAME	 = "<SAGEMAKER_ENDPOINT_NAME>"
    }
  }
}

data "archive_file" "lambda_function_payload" {
  type        = "zip"
  source_dir  = "<source_dire>"
  output_path = "<output_path>"
}

resource "aws_iam_role" "terraform-ml-lambda-execution-role" {
  name               = "terraform-ml-lambda-execution-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "terraform-ml-lambda-execution-policy" {
  name   = "terraform-ml-lambda-execution-policy"
  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "logs:CreateLogGroup",
        Resource = "arn:aws:logs:us-east-1:SECRET_AWS_ACC_ID:*"
      },
      {
        Effect   = "Allow",
        Action   = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = [
          "arn:aws:logs:us-east-1:<SECRET_AWS_ACC_ID>:log-group:/aws/lambda/api-ml-lambda-func:*"
        ]
      },
      {
        Effect   = "Allow",
        Action   = "sagemaker:InvokeEndpoint",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_execution_attachment" {
  role       = aws_iam_role.terraform-ml-lambda-execution-role.name
  policy_arn = aws_iam_policy.terraform-ml-lambda-execution-policy.arn
}
