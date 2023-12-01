# syntax=docker/dockerfile:1.2

ARG DEPS=build

FROM python:3.9-bullseye AS build

ENV PIP_ROOT_USER_ACTION=ignore
RUN apt-get update && apt-get install --yes libgdal-dev
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip setuptools wheel


FROM build AS build-utils
WORKDIR /build/
COPY /dependencies/Utils-Flask-SQLAlchemy .
RUN python setup.py bdist_wheel


FROM build AS build-refgeo
WORKDIR /build/
COPY /dependencies/RefGeo .
RUN python setup.py bdist_wheel


FROM build AS build-usershub-auth-module
WORKDIR /build/
COPY /dependencies/UsersHub-authentification-module .
RUN python setup.py bdist_wheel


FROM build AS build-taxhub
WORKDIR /build/
COPY /setup.py .
COPY /requirements-common.in .
COPY /requirements-dependencies.in .
COPY /VERSION .
COPY /MANIFEST.in .
COPY /README.rst .
COPY /LICENSE .
COPY /apptax ./apptax
COPY /apptax/docker_config.py ./apptax/config.py
RUN python setup.py bdist_wheel


FROM node:alpine AS node

WORKDIR /dist/
COPY /static/package*.json .
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev


FROM python:3.9-bullseye AS app

WORKDIR /dist/

ENV PIP_ROOT_USER_ACTION=ignore

RUN apt-get update && apt-get install --yes libgdal-dev
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip setuptools wheel

COPY --from=node /dist/node_modules ./static/node_modules
COPY /static ./static
RUN mv static/app/constants.js.sample static/app/constants.js

FROM app AS app-build

COPY /requirements-dev.txt .
RUN sed -i 's/^-e .*/# &/' requirements-dev.txt
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements-dev.txt

COPY --from=build-utils /build/dist/*.whl .
COPY --from=build-refgeo /build/dist/*.whl .
COPY --from=build-usershub-auth-module /build/dist/*.whl .


FROM app AS app-pypi

COPY /requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt


FROM app-${DEPS} AS prod

COPY --from=build-taxhub /build/dist/*.whl .
RUN --mount=type=cache,target=/root/.cache \
    pip install *.whl

ENV FLASK_APP=apptax.app:create_app
ENV PYTHONPATH=/dist/config/
ENV TAXHUB_SETTINGS=config.py
ENV TAXHUB_STATIC_FOLDER=/dist/static

EXPOSE 5000

CMD ["gunicorn", "apptax.app:create_app()", "--bind=0.0.0.0:5000", "--access-logfile=-", "--error-logfile=-", "--reload",  "--reload-extra-file=config/config.py"]
