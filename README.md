# Ayesaac

This repository contains the source code for Ayesaac, a Python program to help blind people to find what they have lost in a room.

## Getting started

1. Pull the repo
1. Pull the files in git-lfs using `git-lfs pull`

Install the prerequisites and dependencies following [these instructions](https://github.com/Aye-saac/aye-saac/wiki/Installing-things) if you want to have things running manually. Alternatively, install [Docker](https://docker.com).

### Developing with Docker

Using `make build_image`, you can build an image which will be used for all services required by the system. Then, you can run it using `docker-compose up` and all related services will load up.

When creating the image, [models are downloaded](https://github.com/Aye-saac/aye-saac/blob/1163ff751be4800925af5ee39e1d84f858be9ea5/Dockerfile#L47) and [placed in the right place](https://github.com/Aye-saac/aye-saac/blob/1163ff751be4800925af5ee39e1d84f858be9ea5/Dockerfile#L69) to make life easier.

Note: Because they all need RabbitMQ to work, they will error and restart a bunch of times and then stabilise once RabbitMQ is ready and work properly.

### Architecture

![](docs/diagram_aye-saac_v3.png)
