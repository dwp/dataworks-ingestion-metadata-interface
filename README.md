[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=dwp_dataworks-ingestion-metadata-interface&metric=alert_status)](https://sonarcloud.io/dashboard?id=dwp_dataworks-ingestion-metadata-interface)
# Dataworks Ingestion Metadata Interface

## AWS Lambda to connect to MySQL database, execute query, and return results

This repo contains Makefile to fit the standard pattern.
This repo is a base to create new non-Terraform repos, adding the githooks submodule, making the repo ready for use.

After cloning this repo, please run:  
`make bootstrap`

## Developing locally
To enable you to develop this lambda locally and be able to run it, use the Makefile commands:
`make mysql`
`make env_vars`

This will download and run a MySQL docker container with the same version of the Aurora serverless RDS database.
Will also set the environment variables in your shell appropriately for the lambda to run.
You will be required to gain an AWS STS token before running the script as it calls to Secrets Manager.
