#!/bin/bash
# docker healthcheck TH
url_test=http://localhost:5000${TAXHUB_APPLICATION_ROOT}/
if [ ! -f /tmp/container_healthy ]; then
    curl -f "${url_test}" || exit 1
    touch /tmp/container_healthy
fi