########################################################################
#
# UsersHub  (A GeoNature suite application)
#
#########################################################################

#########################################################################
# Create a Node container which will be used to install the JS libs
#########################################################################

FROM node:12-alpine3.11 AS node-builder

COPY app/static /app/static

WORKDIR /app/static 

RUN npm ci

#########################################################################
# Create a Python container run app
###################################################################

FROM python:3.7-slim-buster

## install dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y locales gcc libpq-dev postgresql-client && \
    localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8 && \
    apt-get clean

## set LANG env
ENV LANG fr_FR.utf8

## set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

## set working directory
WORKDIR /usr/src/app

## add user
RUN addgroup --system -gid 1001 user && adduser --system --no-create-home --uid 1001 --group user

## add and install requirements
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

## Clean apt after requirements install
RUN apt-get autoremove -y gcc
RUN rm -rf /var/lib/apt/lists/* 

COPY . /usr/src/app
RUN chown -R user:user /usr/src/app && chmod -R 755 /usr/src/app

VOLUME ["/usr/src/app/config"]

USER user

# Copy js libs from node builder
COPY --from=node-builder /app/static/node_modules /usr/src/app/app/static/node_modules

EXPOSE 5001

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
