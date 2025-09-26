FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies for hdbscan
RUN yum install -y gcc gcc-c++ make

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY app ./app

# Set the CMD to run FastAPI app with Mangum (ASGI adapter for Lambda)
RUN pip install mangum
CMD ["app.main:app"]
