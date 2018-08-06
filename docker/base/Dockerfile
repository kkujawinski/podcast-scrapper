FROM ubuntu:xenial
MAINTAINER Egyed Zoltán "zoltan.egyed@vertis.com"

RUN echo deb http://ppa.launchpad.net/ionel-mc/socat/ubuntu xenial main > /etc/apt/sources.list.d/ionel-mc-socat-xenial.list \
 && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 88E048443558A630

RUN apt-get update && apt-get -y upgrade
ENV LANG C.UTF-8
RUN set -x && apt-get update && \
              apt-get install -y --no-install-recommends \
                software-properties-common \
                python3 \
                ca-certificates \
                python3-pip \
                python3-setuptools \
                vim \
                curl \
                git \
                wget \
                socat=1.7.3.1-1ionelmc1~ppa1

RUN pip3 install click==6.3

COPY skel /etc/skel
RUN git clone https://github.com/legios89/molokai.git /etc/skel/.vim/
COPY skel/* /root/
COPY runutils.py /usr/local/lib/python3.5/dist-packages/runutils.py

ARG DEVELOPER_UID
ARG DEVELOPER_GID
RUN groupadd -g $DEVELOPER_GID developer && \
      useradd -u $DEVELOPER_UID -g $DEVELOPER_GID -m developer
RUN groupadd -g 5432 postgres && useradd -u 5432 -g 5432 -m postgres
