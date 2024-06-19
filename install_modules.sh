#!/bin/bash

 # Only uncomment this for the first run
  pip install langchain
  pip install langchain_openai
  pip install langchain_anthropic
  pip install streamlit_chat
  pip install configargparse
  pip install langgraph
  pip freeze > requirements.txt

  # read -p "All Modules Installed"