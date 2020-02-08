# Ayesaac

## Getting started

* Installing all the things
    * [Installation instructions (recommended)](https://github.com/Aye-saac/aye-saac/wiki/Installing-things-(Recommended))
    * [Installation instructions (using pip instead of poetry)]()


### Setup with an IDE

As _pyenv-virtualenv_ is like virtualenv, IDEs like PyCharm should work nicely with your environment. I used [this answer from StackOverflow](https://stackoverflow.com/a/51545578) to get my PyCharm working properly. 

### Usage

First, start with:
```
./start_all_services.sh
```
After a few seconds, all the services will run in the background, waiting to do work, some warnings can appear, don't worry, it's just Tensorflow 
saying it doesn't find any compatible GPU or that CUDA is not installed, just ignore it, running Tensorflow 
with the GPU is not mandatory.

Now, we just need to tell the first service that there is job to be done ! 
`send_one_request.py` will ping the first service and the rest will follow (send_one_request.py will be replace in the future):
```
python3 send_one_request.py
```

You can look at the `logs/` directory for the services outputs.

To stop the services you just need to enter the following:
```
./stop_all_services.sh
```

### Architecture

![](ayesaac/data/diagram_aye-saac_v2.png)
