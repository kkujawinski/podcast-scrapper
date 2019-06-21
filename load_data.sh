#!/bin/bash -ex

docker cp dump_configs.json podcastscrapper_django_1:/home/developer
docker exec podcastscrapper_django_1 django-admin loaddata /home/developer/dump_configs.json

# docker exec -it podcastscrapper_django_1 django-admin shell_plus
