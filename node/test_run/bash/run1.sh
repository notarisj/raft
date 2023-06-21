#!/bin/bash

# Change directory to the project root
cd /home/notaris/Documents/git/raft

# Add the project directory to the Python path
export PYTHONPATH="${PYTHONPATH}:/home/notaris/Documents/git/raft"

# Execute run1.py
python3 node/test_run/run1.py
