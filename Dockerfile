# ----------------------------------- Base ----------------------------------- #
FROM python:3.8-slim as base

RUN apt-get update -qq \
	&& apt-get install -y --no-install-recommends \
	curl \
	&& apt-get autoremove -y \
	&& apt-get clean -y

# ---------------------------------- Builder --------------------------------- #
FROM base as builder

RUN apt-get update -qq && \
	apt-get install -y --no-install-recommends \
	git \
	build-essential \
	python3-dev \
	libffi-dev \
	libssl-dev \
	# For PIL
	zlib1g \
	# For opencv
	libsm6 \
	libxext6 \
	libxrender-dev \
	&& apt-get autoremove -y \
	&& apt-get clean -y

# Install Poetry & ensure it is in $PATH
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | POETRY_PREVIEW=1 python
ENV PATH "/root/.poetry/bin:/opt/venv/bin:${PATH}"

# Copy deps information
COPY pyproject.toml poetry.lock /app/

# Instals deps
RUN python -m venv /opt/venv && \
	. /opt/venv/bin/activate && \
	cd /app && \
	pip install --no-cache-dir -U pip setuptools && \
	poetry install --no-dev --no-root --no-interaction && \
	rm -rf dist *.egg-info

# Setup Spacy
RUN python -m spacy download en_core_web_md && \
	python -m spacy link en_core_web_md en


# ---------------------------------- Models ---------------------------------- #
FROM base as models

# Download OCR model
RUN mkdir -p /root/.keras-ocr && ( \
	cd /root/.keras-ocr && \
	curl -L -o craft_mlt_25k.h5 https://github.com/faustomorales/keras-ocr/releases/download/v0.8.4/craft_mlt_25k.h5 && \
	curl -L -o crnn_kurapan.h5 https://github.com/faustomorales/keras-ocr/releases/download/v0.8.4/crnn_kurapan.h5 \
	)

# Download Resnet model
RUN mkdir -p data/resnet && \
	cd data/resnet && \
	curl -L -o saved_model.pb https://www.dropbox.com/s/icr8tftv7i4zdpd/ssd_resnet50_v1_2018_07_03.pb?dl=1

# ---------------------------------- Runner ---------------------------------- #
FROM base as runner

RUN apt-get update -qq && \
	apt-get install -y --no-install-recommends \
	ffmpeg \
	libsm6 \
	libxext6 \
	&& apt-get autoremove -y \
	&& apt-get clean -y

COPY --from=builder /opt/venv /opt/venv
COPY --from=models /root/.keras-ocr /root/.keras-ocr
COPY --from=models /data/resnet /app/data/resnet
COPY . app/

# Add the VirtualEnv to $PATH
ENV PATH="/opt/venv/bin:$PATH"

RUN . /opt/venv/bin/activate

WORKDIR /app
ENV PYTHONPATH=./ayesaac


# Add Entrypoint
RUN chmod +x ./scripts/wait-for-it.sh ./scripts/docker-entrypoint.sh

ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
