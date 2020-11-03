SHELL:=bash
LOCALSTACK_READY=^Ready\.$

APP_NAME=metadatastore

default: help

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## Bootstrap local environment for first use
	@make git-hooks

.PHONY: env_vars
env_vars:  ## Generate environment variables for terminal
	@echo "export ENVIRONMENT=local" > env_vars
	@echo "export APPLICATION=dataworks-ingestion-metadata-interface" >> env_vars
	@echo "export AWS_PROFILE=dataworks-development" >> env_vars
	@echo "export AWS_REGION=eu-west-2" >> env_vars
	@echo "export RDS_ENDPOINT=localhost" >> env_vars
	@echo "export RDS_USERNAME=root" >> env_vars
	@echo "export RDS_DATABASE_NAME=${APP_NAME}" >> env_vars
	@echo "export RDS_PASSWORD_SECRET_NAME=developing/metadatastore/demo_secret_key" >> env_vars
	@echo "export SKIP_SSL=true" >> env_vars
	@echo "Now run: source env_vars"

.PHONY: env_vars_jetbrains
env_vars_jetbrains:  ## Generate environment variables for pasting into JetBrains IDEs
	@echo "ENVIRONMENT=local" > env_vars_jetbrains
	@echo "APPLICATION=dataworks-ingestion-metadata-interface" >> env_vars_jetbrains
	@echo "AWS_PROFILE=dataworks-development" >> env_vars_jetbrains
	@echo "AWS_REGION=eu-west-2" >> env_vars_jetbrains
	@echo "RDS_ENDPOINT=localhost" >> env_vars_jetbrains
	@echo "RDS_USERNAME=root" >> env_vars_jetbrains
	@echo "RDS_DATABASE_NAME=${APP_NAME}" >> env_vars_jetbrains
	@echo "RDS_PASSWORD_SECRET_NAME=developing/metadatastore/demo_secret_key" >> env_vars_jetbrains
	@echo "SKIP_SSL=true" >> env_vars_jetbrains
	@echo "PYTHONUNBUFFERED=1" >> env_vars_jetbrains
	@echo "Now copy contents of env_vars_jetbrains into Run Configuration"

.PHONY: sql
sql:  ## Run MySQL container
	@{ \
		echo "INFO: remove $(APP_NAME) container if exists"; \
		docker rm $(APP_NAME); \
		docker run --name $(APP_NAME) -d -e MYSQL_ROOT_PASSWORD=passw0rd -e MYSQL_DATABASE=${APP_NAME} -p 3306:3306 mysql:5.7; \
	}

.PHONY: git-hooks
git-hooks: ## Set up hooks in .git/hooks
	@{ \
		HOOK_DIR=.git/hooks; \
		for hook in $(shell ls .githooks); do \
			if [ ! -h $${HOOK_DIR}/$${hook} -a -x $${HOOK_DIR}/$${hook} ]; then \
				mv $${HOOK_DIR}/$${hook} $${HOOK_DIR}/$${hook}.local; \
				echo "moved existing $${hook} to $${hook}.local"; \
			fi; \
			ln -s -f ../../.githooks/$${hook} $${HOOK_DIR}/$${hook}; \
		done \
	}

up-metadatastore:
	docker-compose up -d metadatastore

service-metadatastore: up-metadatastore
	@{ \
		while ! docker logs metadatastore 2>&1 | grep "^Version" | grep 3306; do \
			sleep 2; \
			echo Waiting for metadatastore.; \
		done; \
	}

up-localstack:
	docker-compose up -d localstack

service-localstack: up-localstack
	@{ \
		while ! docker logs localstack 2> /dev/null | grep -q $(LOCALSTACK_READY); do \
			echo Waiting for localstack.; \
			sleep 2; \
			done; \
        }

services: up-metadatastore up-localstack service-metadatastore service-localstack

clean:
	rm -rf artifacts build src/dataworks_ingestion_metadata_interface.egg-info/
	rm -f metadata-interface-lambda.zip

.PHONY: build
build:
	@{ \
		pip install -r requirements.txt -t artifacts; \
		mkdir -p artifacts/common artifacts/provisioner_lambda artifacts/query_lambda artifacts/unreconciled_lambda artifacts/resources; \
		cp src/common/*.py artifacts/common; \
		cp src/provisioner_lambda/*.py artifacts/provisioner_lambda; \
		cp src/query_lambda/*.py artifacts/query_lambda; \
		cp src/unreconciled_lambda/*.py artifacts/unreconciled_lambda; \
		cp src/resources/*.sql artifacts/resources; \
		cp AmazonRootCA1.pem artifacts/common; \
		cd artifacts; \
		zip -qq -r ../metadata-interface-lambda.zip *; \
	}

create:
	@{ \
	awslocal lambda create-function \
		--function-name ingestion-metadata-provisioner \
		--role whatever \
		--timeout 900 \
		--runtime python3.8 \
		--zip-file fileb://./metadata-interface-lambda.zip \
		--handler provisioner_lambda.provisioner.handler; \
	}

update:
	@{ \
	awslocal lambda update-function-code \
		--function-name ingestion-metadata-provisioner \
		--publish \
		--zip-file fileb://./metadata-interface-lambda.zip; \
	}

invoke:
	@{ \
		awslocal lambda invoke \
			--function-name ingestion-metadata-provisioner \
			--payload '{ "rds_username": "root", "rds_password": "password", "rds_database_name": "metadatastore",  "rds_endpoint": "metadatastore", "table-name": "ucfs", "partition-count": 8, "environment": "local", "application": "ingestion-metadata-provisioner", "rds_password_secret_name": "phony", "skip_ssl": true }' \
			response.json; \
	}

integration-tests: services
	docker-compose up --build integration-tests


mysql-client:
	docker exec -it metadatastore mysql --user=root --password=password metadatastore
