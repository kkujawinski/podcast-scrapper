FROM podcast_scraper-base

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" | tee -a /etc/apt/sources.list
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
           postgresql-common \
           postgresql-client-common \
           ssl-cert \
    && sed -ri 's/#(create_main_cluster) .*$/\1 = false/' \
       /etc/postgresql-common/createcluster.conf \
    && apt-get install -y --no-install-recommends \
           postgresql-9.4 \
           postgresql-contrib-9.4

ENV PATH /usr/lib/postgresql/9.4/bin:$PATH
