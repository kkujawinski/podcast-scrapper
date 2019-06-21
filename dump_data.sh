#!/bin/bash -ex

django-admin dumpdata podcast.Podcast podcast.PodcastScrapingConfiguration podcast.PodcastScrapingSteps > /home/developer/dump_configs.json

# docker cp podcastscrapper_postgres_1:/home/developer/dump_configs.json /home/deploy
# scp digit11.com:/home/deploy/dump_configs.json ./
