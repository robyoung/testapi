#!/bin/bash

if [[ ! -e auth/client_secrets.json ]]; then
  echo "You need to get a client_secrets.json from your Google API Console";
  exit 1
fi

if [[ ! -e venv/ ]]; then
  virtualenv venv
fi

source venv/bin/activate

pip install -qr requirements.txt

python testapi/load.py