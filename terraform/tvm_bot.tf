# Note: The folder must be prepared (i.e. dependencies inlined) by running
# 'make' in tvm_bot/ first
data "archive_file" "tvm_bot_archive" {
  type        = "zip"
  source_dir  = "tvm_bot"
  output_path = "tvm_bot.zip"
}

# See https://registry.terraform.io/providers/hashicorp/aws/2.34.0/docs/guides/serverless-with-aws-lambda-and-api-gateway
resource "aws_lambda_function" "tvm_bot_lambda" {
  function_name = "tvm_bot"

  filename         = "tvm_bot.zip"
  source_code_hash = data.archive_file.tvm_bot_archive.output_base64sha256

  handler = "lambda_function.lambda_handler"
  runtime = "python3.9"

  role = aws_iam_role.lambda_tvm_bot_exec.arn

  depends_on = [aws_iam_role_policy.logs]

  environment {
    variables = {
      WEBHOOK_SECRET = var.tvm_bot_webhook_secret
      REPO           = var.tvm_bot_repo
      USER           = var.tvm_bot_user
      GITHUB_TOKEN   = var.tvm_bot_github_token
    }
  }
}

# IAM role which dictates what other AWS services the Lambda function
# may access.
resource "aws_iam_role" "lambda_tvm_bot_exec" {
  name = "tvm_bot_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "logs" {
  name = "lambda-logs"
  role = aws_iam_role.lambda_tvm_bot_exec.name
  policy = jsonencode({
    "Statement" : [
      {
        "Action" : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ],
        "Effect" : "Allow",
        "Resource" : "arn:aws:logs:*:*:*",
      }
    ]
  })
}

resource "aws_api_gateway_rest_api" "tvm_bot" {
  name        = "tvm_bot"
  description = "API gateway for tvm_bot lambda"
}


resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.tvm_bot.id
  parent_id   = aws_api_gateway_rest_api.tvm_bot.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.tvm_bot.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.tvm_bot.id
  resource_id = aws_api_gateway_method.proxy.resource_id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.tvm_bot_lambda.invoke_arn
}

resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.tvm_bot.id
  resource_id   = aws_api_gateway_rest_api.tvm_bot.root_resource_id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.tvm_bot.id
  resource_id = aws_api_gateway_method.proxy_root.resource_id
  http_method = aws_api_gateway_method.proxy_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.tvm_bot_lambda.invoke_arn
}

resource "aws_api_gateway_deployment" "tvm_bot" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root,
  ]

  rest_api_id = aws_api_gateway_rest_api.tvm_bot.id
  stage_name  = "webhook"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tvm_bot_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_rest_api.tvm_bot.execution_arn}/*/*"
}
