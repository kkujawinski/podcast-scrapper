DEPLOYMENT
Execute instructions from deploy.sh

DUMP JSON
docker-compose -f podcast-scraper/production-docker-compose.yml exec django django-admin dumpdata auth podcast > production_dump.json

DUMP CONFIGS
docker-compose exec django django-admin dumpdata podcast.podcastscrapingsteps
