# Ayesaac

## Getting started

### Installing things

Because of operating systems, there are slightly different instructions for Windows. However, there are some general instructions that apply to all operating systems. 

*Note: If you wish to know, the details for why certain things are needed are below.*

1. Install [Git LFS](https://github.com/git-lfs/git-lfs/wiki/Installation).
1. Install [Poetry](https://python-poetry.org/docs/)
1. Install [RabbitMQ](https://www.rabbitmq.com/download.html)

#### If you have `bash` (MacOS/Linux/["Windows Subsystem for Linux"](https://docs.microsoft.com/en-us/windows/wsl/install-win10))

**NOTE: THIS IS CURRENTLY UNTESTED**

1. Install [pyenv](https://github.com/pyenv/pyenv) or similar
1. Install [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) WITH the optional steps
1. Clone the repo and navigate to the folder
1. Install recommended python version: `pyenv install python-3.7.5`
1. Create a virtual environment to prevent packages populating your base: `pyenv virutalenv 3.7.5 ayesaac-3.7.5`
1. Set the local python version in the repo folder: `pyenv local ayesaac-3.7.5`
1. Install the dependencies with `poetry install`
1. Done. 

Assuming you followed the ["optional" instructions for pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv#activate-virtualenv), whenever you navigate to the repository in your terminal, it _should_ automatically activate the environment, meaning you shouldn't need to run `pyenv activate` (or something similar).

#### If you don't have `bash` (Windows)

If you don't have bash, consider installing the [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10). If you _really_ don't want to install that **[to be added]**.

### Why you should install the things

* **Git LFS** — This is used because it allows us to store any large files (images/videos/models/etc) within the repository directly. 
* **Poetry** — Used for better dependency management than using `requirements.txt`+`setuptools`+`environment.yml` together. It just helps keep things together and consistent. 
* **pyenv** and **pyenv-virtualenv** — Used to manage different python versions on bash supporting terminals. It's not perfect but it's better than some of the other ones. You're more than welcome to use whatever you wish. 
* **python 3.7** — This is a recommendation for Alana and TensorFlow. 

### Setup with an IDE

As _pyenv-virtualenv_ is like virtualenv, IDEs like PyCharm should work nicely with your environment. I used [this answer from StackOverflow](https://stackoverflow.com/a/51545578) to get my PyCharm working properly. 

### Usage

