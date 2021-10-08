FROM debian:buster

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y wget
RUN apt-get install -y git
RUN apt-get install -y postgresql
RUN apt-get install -y postgresql-contrib
RUN apt-get install -y postgresql-server-dev-11
RUN apt-get install -y postgis-2.5
RUN apt-get install -y postgis
RUN apt-get install -y postgresql-11-postgis-2.5

RUN mkdir /TaxHub
WORKDIR /TaxHub
COPY requirements.txt /TaxHub/
COPY requirements-common.txt /TaxHub/
RUN pip3 install -r requirements.txt
COPY . /TaxHub

RUN wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.6/install.sh | bash

ENTRYPOINT ["sh", "entrypoint.sh"]
EXPOSE 80