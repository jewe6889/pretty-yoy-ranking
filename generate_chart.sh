#!/bin/bash

# Activate virtual environment and run the ranking generator
source venv/bin/activate
python generate_ranking.py "$@"