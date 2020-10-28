SHELL:=bash

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

services:
	docker-compose up -d metadatastore
	@{ \
		while ! docker logs metadatastore 2>&1 | grep "^Version" | grep 3306; do \
			sleep 2; \
			echo Waiting for metadatastore.; \
		done; \
	}

integration-tests: services
	docker-compose up --build integration-tests
