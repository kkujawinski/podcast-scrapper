# coding: utf-8
# Core and 3th party packages
import signal
import time
import click
import psycopg2
import os
from django.conf import settings

# Utils Imports
from runutils import run_daemon, runbash, ensure_dir, getvar, run_cmd


def waitfordb(stopper):
    """ Wait for the database to accept connections. """
    tick = 0.1
    intervals = 100 * [10]
    for i in intervals:
        click.echo('checking connection ...')
        try:
            psycopg2.connect(host='postgres', port=5432, database="django",
                             user="postgres", password=getvar('DB_PASSWORD'))
        except:
            click.echo('could not connect yet')
        else:
            return

        for w in range(i):
            if stopper.stopped:
                return
            time.sleep(tick)





# INIT: WILL RUN BEFORE ANY COMMAND AND START  #
def init(stopper):
    ensure_dir('/data/logs/django', owner='developer', group='developer')
    ensure_dir('/data/static', owner='developer', group='developer')
    

    if not stopper.stopped:
        if settings.DEBUG is False:
            cmd = ['django-admin', 'collectstatic', '--noinput', '-i', 'react']
            run_cmd(cmd, user='developer')
            run_cmd(['django-admin', 'migrate'], user='developer')

        # Create db cache
        if os.path.isfile('/data/.init') is False:
            run_cmd(['django-admin', 'migrate'], user='developer')
            run_cmd(['django-admin', 'createcachetable', '-v', '0'],
                    user='developer')
            with open("/data/.init", "a+") as f:
                f.write('')

        


@click.group()
def run():
    pass


@run.command()
@click.argument('user', default='developer')
def shell(user):
    runbash(user)


@run.command()
def start_runserver():
    start = ['django-admin.py', 'runserver', '0.0.0.0:8000']
    run_daemon(start, signal_to_send=signal.SIGINT, user='developer',
               waitfunc=waitfordb, initfunc=init)


@run.command()
def start_uwsgi():
    """Starts the service."""
    start = ["uwsgi", "--ini", '/config/uwsgi.conf', '--post-buffering', '1']
    run_daemon(start, signal_to_send=signal.SIGQUIT, user='developer',
               waitfunc=waitfordb, initfunc=init)


if __name__ == '__main__':
    run()
