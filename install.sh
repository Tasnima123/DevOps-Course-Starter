#!/bin/bash

sudo apt-get update

sudo apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

exec $SHELL

curl -sSL https://raw.githubusercontent.com/python-poetry/
poetry/master/get-poetry.py | python