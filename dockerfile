# Dependencies available through Docker hub:
FROM rabbitmq:3.8.2
FROM continuumio/miniconda3:latest

# poetry requires a compiler to be installed:
RUN apt-get -y install build-essential

# Dependencies available through aptitude:
RUN apt-get -y install portaudio19-dev
#RUN apt-get -y install python-all-dev

# Clone workspace into this container
WORKDIR /aye-saac
COPY ./environment.yml /aye-saac/environment.yml

# Create environment
RUN conda env create --file environment.yml
# https://pythonspeed.com/articles/activate-conda-dockerfile/
# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "aye-saac", "/bin/bash", "-c"]

#RUN conda activate aye-saac
#RUN conda install python=3.6
#RUN conda install poetry

# Update poetry's package list
#RUN poetry self update --no-interaction
COPY ./pyproject.toml /aye-saac/pyproject.toml
COPY ./poetry.lock /aye-saac/poetry.lock

# Skip using the secret repo, assume it's already cloned inside aye-saac directory (lazy and bad, todo use a better way)
RUN grep -v "alana" pyproject.toml > temp && mv temp pyproject.toml
RUN poetry install

COPY ./secret_alana_utils/ /aye-saac/secret_alana_utils
RUN ls
RUN cd secret_alana_utils/ && pip install -e .

# Fix Windows-style line endings if they appear
COPY ./ayesaac/start_all_services_in_env.sh /aye-saac/ayesaac/start_all_services_in_env.sh
RUN sed -i -e 's/\r//g' /aye-saac/ayesaac/start_all_services_in_env.sh
RUN cat /aye-saac/ayesaac/start_all_services_in_env.sh

# Run app
WORKDIR /aye-saac
COPY . /aye-saac
WORKDIR /aye-saac/ayesaac
RUN ls
ENTRYPOINT ["conda", "run", "-n", "aye-saac", "/bin/bash", "-c", "/aye-saac/ayesaac/start_all_services_in_env.sh"]