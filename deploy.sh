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

cat > ~/.ssh/id_rsa <<EOL
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
EOL
chmod 600 ~/.ssh/id_rsa

cat >> ~/.ssh/known_hosts <<EOL
|1|kUg0KK6qbwiYSbaiMEAaXq8E8Rg=|bPkH332YvBguHlKUSuGhTuUxiVc= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAubiN81eDcafrgMeLzaFPsw2kNvEcqTKl/VqLat/MaB33pZy0y3rJZtnqwR2qOOvbwKZYKiEO1O6VqNEBxKvJJelCq0dTXWT5pbO2gDXC6h6QDXCaHo6pOHGPUy+YBaGQRGuSusMEASYiWunYN0vCAI8QaXnWMXNMdFP3jHAJH0eDsoiGnLPBlBp4TNm6rYI74nMzgz3B9IikW4WVK+dc8KZJZWYjAuORU3jc1c/NPskD2ASinf8v3xnfXeukU0sJ5N6m5E8VLjObPEO+mN2t/FZTMZLiFqPWc/ALSqnMnnhwrNi2rbfg/rd/IpL8Le3pSBne8+seeFVBoGqzHM9yXw==
|1|VGKR1Qd4Duk7+3jBMOyt2IFB010=|6xGmMbepRSadu+Cfu0EB49o4IVs= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAubiN81eDcafrgMeLzaFPsw2kNvEcqTKl/VqLat/MaB33pZy0y3rJZtnqwR2qOOvbwKZYKiEO1O6VqNEBxKvJJelCq0dTXWT5pbO2gDXC6h6QDXCaHo6pOHGPUy+YBaGQRGuSusMEASYiWunYN0vCAI8QaXnWMXNMdFP3jHAJH0eDsoiGnLPBlBp4TNm6rYI74nMzgz3B9IikW4WVK+dc8KZJZWYjAuORU3jc1c/NPskD2ASinf8v3xnfXeukU0sJ5N6m5E8VLjObPEO+mN2t/FZTMZLiFqPWc/ALSqnMnnhwrNi2rbfg/rd/IpL8Le3pSBne8+seeFVBoGqzHM9yXw==
EOL

git clone git@bitbucket.org:kkujawinski/podcast-scraper.git

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