#!/bin/bash
# NOTE: You only need to run this once.
# conda create -n quanta_agent python=3.11.5

source activate quanta_agent
# conda activate quanta_agent <--- this command randomly fails, so we use source activate instead
streamlit run Quanta_Agent.py