#!/bin/bash

# Add the project directory to the Python path
export PYTHONPATH="${PYTHONPATH}:${pwd}"

# Store the command to be executed
command="python3 src/raft_node/deploy/run_server.py"

# Parse command-line arguments
while [[ $# -gt 1 ]]; do
    key="$1"
    case $key in
        --server_id)
            server_id="$2"
            shift 2
            ;;
        --uvicorn_host)
            uvicorn_host="$2"
            shift 2
            ;;
        --uvicorn_port)
            uvicorn_port="$2"
            shift 2
            ;;
        --mongo_host)
            mongo_host="$2"
            shift 2
            ;;
        --mongo_port)
            mongo_port="$2"
            shift 2
            ;;
        --mongo_db_name)
            mongo_db_name="$2"
            shift 2
            ;;
        --mongo_collection_name)
            mongo_collection_name="$2"
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
