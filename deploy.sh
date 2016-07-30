sudo yum update -y
sudo yum install -y docker git
sudo yum install -y mailx
sudo yum install -y sendmail
sudo service docker start
sudo service sendmail start
sudo usermod -a -G docker ec2-user
sudo su ec2-user
sudo pip install docker-compose

echo 'export PATH="$PATH:/usr/local/bin"' >> ~/.bashrc

git clone https://github.com/kkujawinski/podcast-scrapper.git

cd podcast-scraper

./buildall.sh

cat > env.txt <<EOL
DJANGO_SECRET_KEY=
DB_PASSWORD=
DEBUG=False
ALLOWED_HOSTS=
YANDEX_TRANSLATE_KEY=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
STATIC_ROOT=/data/static/
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET=
AWS_REGION_NAME=
AWS_SIGNATURE_VERSION=
SCRAP_BATCH=3
SCRAP_BATCH_INTERVAL=2
EOL

read -n1 -r -p "Fill env.txt and press any key to continue" key

sudo tee /etc/init.d/podcastscraper <<"EOL"
#!/bin/sh

### BEGIN INIT INFO
# Provides:     podcastscraper
# Required-Start:   $docker
# Required-Stop:    $docker
# Default-Start:    2 3 4 5
# Default-Stop:     0 1 6
# Short-Description:    Docker Services
### END INIT INFO

set -e

PROJECT_NAME=podcastscraper
YAMLFILE=/home/ec2-user/podcast-scraper/production-docker-compose.yml
OPTS="-f $YAMLFILE -p $PROJECT_NAME"
UPOPTS="-d --no-recreate --no-build --no-deps"
DOCKER_COMPOSE=/usr/local/bin/docker-compose

case "$1" in
    forcestart)
        echo "Starting Docker Compose"
        $DOCKER_COMPOSE $OPTS up -d --force-recreate
        ;;

    start)
        echo "Starting Docker Compose"
        $DOCKER_COMPOSE $OPTS up $UPOPTS
        ;;

    stop)
        echo "Stopping Docker Compose"
        $DOCKER_COMPOSE $OPTS stop
        ;;

    reload)
        echo "Reloading Docker Compose"
        $DOCKER_COMPOSE $OPTS up $UPOPTS
        ;;

    restart)
        $DOCKER_COMPOSE $OPTS stop
        $DOCKER_COMPOSE $OPTS up $UPOPTS
        ;;

    *)
        echo "Usage: /etc/init.d/podcastscraper {start|stop|restart|reload|forcestart}"
        exit 1
        ;;
esac

exit 0
EOL
sudo chmod 755 /etc/init.d/podcastscraper

sudo service podcastscraper start

crontab <<"EOL"
MAILTO=kamil@kujawinski.net

# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7)  OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  *  command to be executed

  5  *  *  *  *  /home/ec2-user/podcast-scraper/worker-docker-run.py
EOL
