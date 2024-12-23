# Base image with Python
FROM google/cloud-sdk:slim

RUN apt-get update && apt-get install -y python3-venv

# Set working directory
WORKDIR /app

# Install virtualenv
#RUN pip3 install virtualenv

# Create and activate a virtual environment
RUN python3 -m venv /venv 

# Use bash explicitly to enable the `source` command
SHELL ["/bin/bash", "-c"]
RUN source /venv/bin/activate

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    && rm -rf /var/lib/apt/lists/*

# Make the virtual environment available in subsequent layers
ENV PATH="/venv/bin:$PATH"

# THIS DOES NOT WORK
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY} 
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV SEMANTIC_SCHOLAR_API_KEY=${SEMANTIC_SCHOLAR_API_KEY}
# ^ does not work rn

# Install Python dependencies
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy the application code
COPY . .

# Expose ports (if needed for debugging or monitoring)
EXPOSE 6379
# For Flower monitoring (optional)
EXPOSE 5555 

# Default command to run the Celery worker
CMD ["/venv/bin/celery", "-A", "celery_app", "worker", "--loglevel=info"]
