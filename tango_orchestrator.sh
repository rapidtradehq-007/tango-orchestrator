#!/bin/bash
set -e
docker build -t tango-reseller-bot .
docker run -it \
  --env-file .env \
  tango-reseller-bot
