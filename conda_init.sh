#!/bin/bash

conda_path="/home/clay/miniconda3"
export PATH="$conda_path/bin:$PATH"

if ! conda env list | grep -q "quanta_agent"; then
  echo "Creating Conda Environment: quanta_agent"
  conda create -n quanta_agent python=3.12.3
  ./install_modules.sh
fi

source $conda_path/bin/activate quanta_agent