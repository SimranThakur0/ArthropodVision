#!/bin/bash

# Define the virtual environment name (change if desired)
VENV_NAME="myvenv"

# Check if virtualenv is installed
if ! command -v virtualenv &> /dev/null; then
  echo "Virtualenv is not installed. Please install it first."
  exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
  echo "requirements.txt file not found. Please create one with your project dependencies."
  exit 1
fi

# Create virtual environment
echo "Creating virtual environment: $VENV_NAME"
python3 -m venv $VENV_NAME

# Activate virtual environment (adjust for your shell)
source $VENV_NAME/bin/activate  # For bash/zsh
# . $VENV_NAME/bin/activate        # For fish shell

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt

# Print success message
echo "Virtual environment created and dependencies installed!"
echo "Activate the environment using 'source $VENV_NAME/bin/activate' (or similar for your shell)."