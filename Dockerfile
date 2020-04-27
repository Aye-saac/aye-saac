FROM python:3.6.10-slim as python_builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    # For ASR
    portaudio19-dev \
    # For PIL
    zlib1g \
    # For opencv
    libsm6 \
    libxext6 \
    libxrender-dev
# remove apt cache to reduce image size
# && rm -rf /var/lib/apt/lists/*

# Install keras-ocr models
RUN mkdir -p /root/.keras-ocr && ( \
    cd /root/.keras-ocr && \
    curl -L -o craft_mlt_25k.pth https://www.mediafire.com/file/qh2ullnnywi320s/craft_mlt_25k.pth/file && \
    curl -L -o craft_mlt_25k.h5 https://www.mediafire.com/file/mepzf3sq7u7nve9/craft_mlt_25k.h5/file && \
    curl -L -o crnn_kurapan.h5 https://www.mediafire.com/file/pkj2p29b1f6fpil/crnn_kurapan.h5/file \
    )



# Install Poetry & ensure it is in $PATH
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | POETRY_PREVIEW=1 python
ENV PATH "/root/.poetry/bin:/opt/venv/bin:${PATH}"

# Copy deps information
COPY pyproject.toml poetry.lock /opt/ayesaac/

# Install deps
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    cd /opt/ayesaac && \
    pip3 install -U pip && \
    poetry export --without-hashes -f requirements.txt | grep -v "alana" | grep -v "tensorflow-estimator" > requirements.txt && \
    pip install cython && \
    pip install setuptools==41.0.1 && \
    pip install tensorflow-estimator==2.1.0 && \
    pip install -r requirements.txt


# Main container (without previous bloat)
FROM python:3.6.10-slim

# Copy built deps from base build
COPY --from=python_builder /opt /opt

# Copy KerasOCR models from builder
COPY --from=python_bulder /root/.keras-ocr /root/.keras-ocr

RUN apt-get update && apt-get -y install \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0
# remove apt cache to reduce image size
# && rm -rf /var/lib/apt/lists/*
# Add the VirtualEnv to the beginning of $PATH
ENV PATH="/opt/venv/bin:$PATH"

# Install from alana utils
COPY ./secret_alana_utils /opt/ayesaac/secret_alana_utils
RUN . /opt/venv/bin/activate && \
    cd /opt/ayesaac/secret_alana_utils && \
    pip install -e .

# Copy project files
COPY ayesaac/ /opt/ayesaac/ayesaac

WORKDIR /opt/ayesaac
ENV PYTHONPATH=./ayesaac

RUN echo "Removing previous logs" && \
    rm -fv ayesaac/services_log/*.txt

RUN echo "Clean output folder" && \
    rm -fv output/*.txt && \
    mkdir output

COPY scripts/wait-for-it.sh wait-for-it.sh
RUN chmod +x wait-for-it.sh

# ENTRYPOINT ["/bin/bash"]
# CMD ["./wait-for-it.sh", "rabbitmq:5672", "--timeout=100", "--", "./ayesaac/start_all_services_in_container.sh"]