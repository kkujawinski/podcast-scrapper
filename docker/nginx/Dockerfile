FROM podcast_scraper-base

RUN curl http://nginx.org/keys/nginx_signing.key | apt-key add -
RUN echo "deb http://nginx.org/packages/debian/ jessie nginx" | tee -a /etc/apt/sources.list
RUN echo "deb-src http://nginx.org/packages/debian/ jessie nginx" | tee -a /etc/apt/sources.list
RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
        nginx
