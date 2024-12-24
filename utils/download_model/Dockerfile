FROM python:3.12-slim

# Install zip utility
RUN apt-get update && apt-get install -y zip && apt-get clean

# Define a default build argument
ARG MODEL_LOCATION=saved_model

# Set the working directory
WORKDIR /pyhton

# Copy requirements and install dependencies
RUN pip install sentence-transformers

# Copy python function
COPY download_model.py .

RUN python download_model.py ${MODEL_LOCATION}


