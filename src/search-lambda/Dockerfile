FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies for hdbscan
RUN dnf install -y gcc gcc-c++ make

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app ./app

# Command: Lambda will invoke `handler` in `app.main`
CMD ["app.main.handler"]
