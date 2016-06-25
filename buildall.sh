#!/bin/bash -eEx
if [[ "$(uname)" == "Darwin" ]]; then
    USER_UID=1000
    USER_GID=1000
else
    USER_UID="$(id -u)"
    USER_GID="$(id -u)"
fi


echo "base"
echo "--------------------"
docker build \
  --build-arg "DEVELOPER_UID=$USER_UID" \
  --build-arg "DEVELOPER_GID=$USER_GID" \
  -t podcast_scraper-base "docker/base"

echo "postgres"
echo "--------------------"
docker build -t podcast_scraper-postgres "docker/postgres"

echo "nginx"
echo "--------------------"
docker build -t podcast_scraper-nginx "docker/nginx"

echo "django-python3"
echo "--------------------"
docker build \
  -t podcast_scraper-django-python3 "docker/django-python3"

# echo "periodic-tasks"
# echo "--------------------"
# docker build \
#   -t podcast_scraper-django-python3 "docker/django-python3"


echo 'Start the data container'
echo "--------------------"
docker-compose --file data-docker-compose.yml up -d
