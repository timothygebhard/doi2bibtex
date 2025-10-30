#!/bin/bash
# Script to run all tests locally
# NOTE: This script must be run from the project root directory

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
pytest tests/ -v "$@"
