#!/bin/bash

init() {
  . ./venv/bin/activate
}

function_name() {
  echo ingestion-metadata-provisioner
}

aws_local() {
  aws --endpoint-url="http://localstack:4566" --region eu-west-2 "$@"
}

configure_cli() {
  aws configure set aws_access_key_id test
  aws configure set aws_secret_access_key test
  aws configure set default.region eu-west-2
  aws configure set region eu-west-2
}

query_function() {
  aws_local \
  lambda list-functions \
  --query "(Functions[?FunctionName=='$(function_name)'])[0].FunctionName" |
  tr -d '"'
}

function_exists() {
  result=$(query_function)
  [[ $result == $(function_name) ]]
}

create_function() {
  aws_local \
    lambda create-function \
    --function-name $(function_name) \
    --role whatever \
    --timeout 900 \
    --runtime python3.8 \
    --zip-file fileb://./metadata-interface-lambda.zip \
    --handler provisioner_lambda.provisioner.handler
}

update_function() {
  aws_local \
      lambda update-function-code \
      --function-name $(function_name) \
      --publish \
      --zip-file fileb://./metadata-interface-lambda.zip
}

run_tests() {
  behave --no-capture --no-capture-stderr ./integration/features/
}
