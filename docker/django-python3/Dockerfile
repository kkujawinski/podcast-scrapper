FROM podcast_scraper-base

RUN set -x && apt-get update && \
              apt-get install -y --no-install-recommends \
                libpq5 \
                libpython3.5 \
                libpq-dev \
                libxslt-dev \
                libxml2-dev \
                build-essential \
                python3-dev \
                xvfb \
                firefox=50.1.0+build2-0ubuntu0.16.04.1

RUN pip3 install \
      uwsgi==2.0.13.1 \
      django==1.9.7 \
      psycopg2==2.6.1 \
      djangorestframework==3.3.3 \
      markdown==2.6.6 \
      django-filter==0.13.0 \
      django-crispy-forms==1.6.0 \
      django-cleanup==0.4.2 \
      django-extensions==1.6.7 \
      django-compressor==2.0 \
      django-cors-middleware==1.2.0 \
      "git+git://github.com/sin5/django-jsoneditor.git@fc79bf852e9de98accccfcdffe59612f890f87c2" \
      pyvirtualdisplay==0.2 \
      selenium==2.53.5 \
      lxml==3.6.0 \
      beautifulsoup4==4.4.1 \
      boto3==1.3.1 \
      temp-utils==1.0.0 \
      remote_pdb

COPY geckodriver-0.8.0-linux64 /usr/local/bin/wires

WORKDIR /src/
