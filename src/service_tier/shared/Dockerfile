FROM python:3.12-slim

# Install zip utility
RUN apt-get update && apt-get install -y zip && apt-get clean

# Set the working directory
WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt -t python/

# Copy shared module
COPY shared/ python/shared/

# Ensure the layer content is structured correctly
RUN mkdir -p /build/layer && mv python /build/layer/python

# The resulting zip will be placed in /build/layer.zip
WORKDIR /build/layer
RUN zip -r /build/layer.zip .
