#!/bin/bash

echo "=======install scrapy under ubuntu=========="
sudo apt-get install libxml2-dev
sudo apt-get install libxslt-dev
sudo apt-get install python-dev
sudo apt-get install libffi-dev
sudo apt-get install libssl-dev

echo "=======install scrapy under ubuntu=========="
virtualenv venc
source  venc/bin/activate
pip install -r requirement
