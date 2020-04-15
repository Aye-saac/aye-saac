#!/usr/bin/env bash

docker-compose down
docker-compose build

docker-compose up &
docker save f21ca-ayesaac_ayesaac > ayesaac.tar &
wait
docker-compose down