#!/bin/bash

. ./environment.sh

init

configure_cli

if function_exists; then
  update_function
else
  create_function
fi

run_tests
