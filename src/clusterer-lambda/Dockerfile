FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm


COPY . ${LAMBDA_TASK_ROOT}

ENV HOME=/tmp
# ENV TRANSFORMERS_CACHE=/tmp
ENV HF_HOME=/tmp

CMD [ "service_dispatcher.handler" ]
