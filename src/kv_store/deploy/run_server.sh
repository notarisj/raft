#!/bin/bash

# Check if the directory path argument is provided
if [ -z "$1" ]; then
    echo "Directory path argument is missing."
    echo "Usage: ./run_server.sh <directory_path> [options]"
    echo "Options:"
    echo "  --server_id <server_id>"
    echo "  --replication_factor <uvicorn_host>"
    exit 1
fi

# Change directory to the provided path
# shellcheck disable=SC2164
cd "$1"

# Add the project directory to the Python path
export PYTHONPATH="${PYTHONPATH}:$1"

# Store the command to be executed
command="python3 src/kv_store/deploy/run_server.py"

# Parse command-line arguments
while [[ $# -gt 1 ]]; do
    key="$2"
    case $key in
        --server_id)
            server_id="$3"
            shift 2
            ;;
        --replication_factor)
            replication_factor="$3"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Add the arguments to the command if they are provided
if [ -n "$server_id" ]; then
    command+=" --server_id $server_id"
fi

if [ -n "$replication_factor" ]; then
    command+=" --replication_factor $replication_factor"
fi

# Execute the command
eval "$command"
