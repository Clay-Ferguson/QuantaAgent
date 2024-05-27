#!/bin/bash

# NOTE: You only need to run this once.
# conda create -n quanta_agent python=3.11.5

conda_path="/home/clay/miniconda3"
export PATH="$conda_path/bin:$PATH"
source $conda_path/bin/activate quanta_agent

if [[ "$CONDA_DEFAULT_ENV" == "quanta_agent" ]]; then
  python3 quanta-agent.py
else
  echo "Failed to set Conda Environment: Expected quanta_agent but found $CONDA_DEFAULT_ENV"
  sleep 10s
  exit 1
fi

