# syntax=docker/dockerfile:1.2

FROM python:3.9-bullseye AS build

ENV PIP_ROOT_USER_ACTION=ignore
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip setuptools wheel

WORKDIR /dist/taxhub
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


FROM python:3.9-bullseye AS prod

WORKDIR /dist/

ENV PIP_ROOT_USER_ACTION=ignore
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip setuptools wheel

COPY --from=node /dist/node_modules ./static/node_modules

COPY /requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

COPY /static ./static

COPY /requirements-common.in .
COPY /requirements-dependencies.in .
COPY --from=build /dist/taxhub/dist/taxhub-*.whl .
RUN --mount=type=cache,target=/root/.cache \
    pip install taxhub-*.whl

ENV FLASK_APP=apptax.app:create_app
ENV PYTHONPATH=/dist/config/
ENV TAXHUB_SETTINGS=config.py
ENV TAXHUB_STATIC_FOLDER=/dist/static

EXPOSE 5000

CMD ["gunicorn", "apptax.app:create_app()", "--bind=0.0.0.0:5000", "--access-logfile=-", "--error-logfile=-"]
