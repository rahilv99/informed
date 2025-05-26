FROM public.ecr.aws/lambda/python:3.12

# Install system package
# Download and install a static build of ffmpeg
# RUN curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz | tar xJ && \
#     mv ffmpeg-*-static/ffmpeg /usr/local/bin/ && \
#     mv ffmpeg-*-static/ffprobe /usr/local/bin/ && \
#     rm -rf ffmpeg-*-static

# Copy the local saved package folder into the container

# Copy requirements.txt
#COPY src/service_tier/requirements.txt ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm


COPY . ${LAMBDA_TASK_ROOT}
RUN mv ${LAMBDA_TASK_ROOT}/extra_pkgs/ffmpeg-*-static/ffmpeg /usr/local/bin/ && \
    mv ${LAMBDA_TASK_ROOT}/extra_pkgs/ffmpeg-*-static/ffprobe /usr/local/bin/ && \
    rm -rf ${LAMBDA_TASK_ROOT}/extra_pkgs/ffmpeg-*-static

ENV HOME=/tmp
# ENV TRANSFORMERS_CACHE=/tmp
ENV HF_HOME=/tmp

CMD [ "service_dispatcher.handler" ]
