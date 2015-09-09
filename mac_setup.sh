#!/bin/bash

echo "mac安装scrapy依赖"
brew install libffi
brew unlink libxml2
brew unlink libxslt
brew install libxml2
brew install libxslt
brew link libxml2 --force
brew link libxslt --force

echo "创建python虚拟环境 安装scrapy"
virtualenv venc
source venc/bin/activate
pip install -r requirements
echo "安装成功"
