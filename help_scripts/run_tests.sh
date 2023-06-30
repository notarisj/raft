#!/bin/bash

# Add the project directory to the Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Store the command to be executed
command="python3 -m unittest discover -p 'test_*.py' -s tests"

# Execute the command
eval "$command"