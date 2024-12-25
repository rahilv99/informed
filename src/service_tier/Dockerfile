FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
#COPY src/service_tier/requirements.txt ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy code
# COPY src/service_tier/email ${LAMBDA_TASK_ROOT}
# COPY src/service_tier/note ${LAMBDA_TASK_ROOT}
# COPY src/service_tier/research ${LAMBDA_TASK_ROOT}
# COPY src/service_tier/saved_model ${LAMBDA_TASK_ROOT}
COPY email ${LAMBDA_TASK_ROOT}/email
COPY note ${LAMBDA_TASK_ROOT}/note
COPY research ${LAMBDA_TASK_ROOT}/research
COPY saved_model ${LAMBDA_TASK_ROOT}/saved_model

# Set the HOME environment variable to somewhere writable for PubMed
ENV HOME=/tmp
ENV TRANSFORMERS_CACHE=/tmp
ENV HF_HOME=/tmp

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "research.discover.handler" ]