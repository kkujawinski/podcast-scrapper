#!/usr/bin/env python

import sys
from subprocess import call
from os.path import dirname, realpath

current_dir = dirname(realpath(__file__))
extra_args = sys.argv[1:]
container_cmd = ["python3", "/config/run.py", "start_worker"]
# container_cmd = ["bash"]

cmd = [
    "docker",
    "run",
    "--user", "developer",
    "--memory", "800M",
    "--volume", current_dir + "/src:/src",
    "--volume", current_dir + "/docker/django-python3/config:/config",
    "--volume", current_dir + "/container_shared:/container_shared",
    "--volumes-from", "podcastscraper_proxy_1",
    "--env", "PYTHONPATH=/src",
    "--env", "DJANGO_SETTINGS_MODULE=core.settings",
    "--env", "PYTHONUNBUFFERED=true",
    "--env-file", current_dir + "/env.txt",
    "--link", "podcastscraper_postgres_1:postgres",
    "--rm",
] + extra_args + [
    "podcast_scraper-django-python3",
] + container_cmd

call(cmd)
