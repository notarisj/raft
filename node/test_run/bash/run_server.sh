#!/bin/bash

# Check if the directory path argument is provided
if [ -z "$1" ]; then
    echo "Directory path argument is missing."
    echo "Usage: ./run_server.sh <directory_path> [options]"
    echo "Options:"
    echo "  --server_id <server_id>"
    echo "  --uvicorn_host <uvicorn_host>"
    echo "  --uvicorn_port <uvicorn_port>"
    echo "  --mongo_host <mongo_host>"
    echo "  --mongo_port <mongo_port>"
    echo "  --mongo_db_name <mongo_db_name>"
    echo "  --mongo_collection_name <mongo_collection_name>"
    exit 1
fi

# Change directory to the provided path
# shellcheck disable=SC2164
cd "$1"

# Add the project directory to the Python path
export PYTHONPATH="${PYTHONPATH}:$1"

# Store the command to be executed
command="python3 node/test_run/run_server.py"

# Parse command-line arguments
while [[ $# -gt 1 ]]; do
    key="$2"
    case $key in
        --server_id)
            server_id="$3"
            shift 2
            ;;
        --uvicorn_host)
            uvicorn_host="$3"
            shift 2
            ;;
        --uvicorn_port)
            uvicorn_port="$3"
            shift 2
            ;;
        --mongo_host)
            mongo_host="$3"
            shift 2
            ;;
        --mongo_port)
            mongo_port="$3"
            shift 2
            ;;
        --mongo_db_name)
            mongo_db_name="$3"
            shift 2
            ;;
        --mongo_collection_name)
            mongo_collection_name="$3"
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

if [ -n "$uvicorn_host" ]; then
    command+=" --uvicorn_host $uvicorn_host"
fi

if [ -n "$uvicorn_port" ]; then
    command+=" --uvicorn_port $uvicorn_port"
fi

if [ -n "$mongo_host" ]; then
    command+=" --mongo_host $mongo_host"
fi

if [ -n "$mongo_port" ]; then
    command+=" --mongo_port $mongo_port"
fi

if [ -n "$mongo_db_name" ]; then
    command+=" --mongo_db_name $mongo_db_name"
fi

if [ -n "$mongo_collection_name" ]; then
    command+=" --mongo_collection_name $mongo_collection_name"
fi

# Execute the command
eval "$command"
