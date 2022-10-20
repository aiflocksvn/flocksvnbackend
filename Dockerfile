FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y lsb-release
RUN apt-get install -y wget
RUN apt-get install -y gnupg2
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update -y
RUN apt-get install  postgresql-client-14  -y
RUN apt-get install -y nano
RUN apt-get install -y gettext
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-pip
RUN apt-get install -y libpq-dev
RUN apt-get install  -y python3.9

RUN mkdir  /eb_system
WORKDIR /eb_system
COPY . .
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements/production.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
