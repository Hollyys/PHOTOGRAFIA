#!/bin/bash

set -e

sudo apt update
sudo apt install -y python3 python3-pip python3-venv

echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment 'venv' created."
else
    echo "Virtual environment 'venv' already exists."
fi

source venv/bin/activate

echo "Virtual environment activated."

pip install --upgrade pip
pip install flask flask-sqlalchemy

echo "Flask and Flask-SQLAlchemy installed."

pip freeze | grep -E 'Flask|SQLAlchemy'

echo "Back-End setup completed. To activate the virtual environment later, run 'source venv/bin/activate'."
