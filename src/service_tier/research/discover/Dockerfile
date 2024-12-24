FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY src/service_tier/research/discover/requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY src/service_tier/shared/user_topics.py ${LAMBDA_TASK_ROOT}
COPY src/service_tier/research/discover/main.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handler" ]