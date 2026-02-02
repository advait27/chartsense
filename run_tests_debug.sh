#!/bin/bash
export PATH=$PWD/.venv/bin:$PATH
pip install -r requirements.txt
pytest tests/ > test_results.txt 2>&1
echo "Done" >> test_results.txt
