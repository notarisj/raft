#!/bin/bash

# Add the project directory to the Python path
export PYTHONPATH="${PYTHONPATH}:${pwd}"

# Store the command to be executed
command="python3 src/kv_store/deploy/run_server.py"

# Parse command-line arguments
while [[ $# -gt 1 ]]; do
    key="$1"
    case $key in
        --server_id)
            server_id="$2"
            shift 2
            ;;
        --replication_factor)
            replication_factor="$2"
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
