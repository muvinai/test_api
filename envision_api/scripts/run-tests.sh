#!/bin/sh

docker compose up --build --abort-on-container-exit --attach python-api --no-log-prefix
