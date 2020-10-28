[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=dwp_dataworks-ingestion-metadata-interface&metric=alert_status)](https://sonarcloud.io/dashboard?id=dwp_dataworks-ingestion-metadata-interface)
[![Known Vulnerabilities](https://snyk.io/test/github/dwp/dataworks-ingestion-metadata-interface/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dwp/dataworks-ingestion-metadata-interface?targetFile=requirements.txt)
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

## Tests

There are `tox` unit tests in the module. 
To run them, you will need the module `tox` installed with `pip install tox`, then go to the root of the module and simply run `tox` to run all the unit tests. 
You should always ensure they work before making a pull request for your branch.

If `tox` has an issue with Python version you have installed, you can specify such as `tox -e py38`.

## Lambda deployment

This code is deployed as two separate lambdas via the `aws-ingestion` repository.

### Provisioner lambda

This lambda sets up the tables on RDS and the code can be found in the `provisioner.py` script. The handler method is how the lambda is called when invoked on AWS.

### Query lambda

This lambda queries the given table on RDS and the code can be found in the `query.py` script. The handler method is how the lambda is called when invoked on AWS.

### Unreconciled lambda

This lambda has two queries for the Metadata Store to allow for logging of important results. The two queries used are:
- Unreconciled and Reconciled counts
- Unreconciled after Max Age

The code can be found in the `unreconciled.py` script. The handler method is how the lambda is called when invoked on AWS.
