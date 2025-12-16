FROM python:3.10-slim-bookworm

# Update system and install packages
RUN apt update &&\
    apt upgrade -y &&\
    apt autoremove -y &&\
    apt -y install \
        tesseract-ocr-ces \
        libenchant-2-2

# Upgrade python package manager
RUN pip install pdm

# Create working directory
RUN mkdir -p /opt/lunch-bot

# Change working directory
WORKDIR /opt/lunch-bot

# Copy folders and files – It's important to copy files before changing their ownership
COPY ./pyproject.toml ./pyproject.toml
COPY ./src ./src
COPY ./main.py ./main.py

# Install dependencies
RUN pdm install

# Command on start of container
CMD bash -c "eval \$(python3 -m pdm venv activate in-project) && python3 main.py"
