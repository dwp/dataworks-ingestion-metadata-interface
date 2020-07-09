SHELL:=bash

APP_NAME=metadatastore

default: help

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## Bootstrap local environment for first use
	@make git-hooks

.PHONY: git-hooks
git-hooks: ## Set up hooks in .githooks
	@git submodule update --init .githooks ; \
	git config core.hooksPath .githooks \

.PHONY: mysql
mysql:  ## Run MySQL container
	@{ \
		echo "INFO: remove $(APP_NAME) container if exists"; \
		docker rm $(APP_NAME); \
		docker run --name $(APP_NAME) -d -e MYSQL_ROOT_PASSWORD=passw0rd -e MYSQL_DATABASE=${APP_NAME} -p 3306:3306 mysql:5.7; \
	}

.PHONY: env_vars
env_vars:  ## Display environment variables
	@echo "export ENVIRONMENT=local" > env_vars
	@echo "export APPLICATION=dataworks-ingestion-metadata-interface" >> env_vars
	@echo "export AWS_PROFILE=dataworks-development" >> env_vars
	@echo "export AWS_REGION=eu-west-2" >> env_vars
	@echo "export RDS_ENDPOINT=localhost" >> env_vars
	@echo "export RDS_USERNAME=root" >> env_vars
	@echo "export RDS_DATABASE_NAME=${APP_NAME}" >> env_vars
	@echo "export RDS_PASSWORD_SECRET_NAME=developing/metadatastore/demo_secret_key" >> env_vars
	@echo "Now run: source env_vars"
