#!/bin/bash

# Check if the directory path argument is provided
if [ -z "$1" ]; then
    echo "Directory path argument is missing."
    echo "Usage: ./run_client.sh <directory_path>"
    exit 1
fi

# Change directory to the provided path
# shellcheck disable=SC2164
cd "$1"

# Add the project directory to the Python path
export PYTHONPATH="${PYTHONPATH}:$1"

# Store the command to be executed
command="python3 src/kv_store/client/client1.py"

# Execute the command
eval "$command"
