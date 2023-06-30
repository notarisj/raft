#!/bin/bash

# Add the project directory to the Python path
export PYTHONPATH="${PYTHONPATH}:${pwd}"

# Store the command to be executed
command="python3 src/raft_node/cli/cli.py"

# Execute the command
eval "$command"
