#!/usr/bin/env python

import sys
from subprocess import call
from os.path import dirname, realpath

current_dir = dirname(realpath(__file__))
extra_args = sys.argv[1:]
container_cmd = ["python3", "/config/run.py", "rerun_worker"]
# container_cmd = ["bash"]


cmd = [
    "docker",
    "run",
    "--user", "developer",
    "--memory", "700MB",
    "--cpu-period", "50000",
    "--cpu-quota", "9000",
    "--volume", current_dir + "/src:/src",
    "--volume", current_dir + "/docker/django-python3/config:/config",
    "--volume", current_dir + "/container_shared:/container_shared",
    "--volumes-from", "podcastscrapper_proxy_1",
    "--env", "PYTHONPATH=/src",
    "--env", "DJANGO_SETTINGS_MODULE=core.settings",
    "--env", "PYTHONUNBUFFERED=true",
    "--env", "SCRAP_BATCH=10",
    "--env", "SCRAP_BATCH_INTERVAL=0",
    "--env-file", current_dir + "/env.txt",
    "--link", "podcastscrapper_postgres_1:postgres",
    "--rm",
    "podcast_scraper-django-python3",
] + container_cmd + extra_args

call(cmd)
