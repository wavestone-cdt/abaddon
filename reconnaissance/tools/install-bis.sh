#!/bin/bash
HOME_EC2="/home/ec2-user"
GOPHISH_DIR="$HOME_EC2/Gophish"
GOPHISH_VERSION="0.7.1"
mkdir -p $GOPHISH_DIR
cd $GOPHISH_DIR
wget https://github.com/gophish/gophish/releases/download/$GOPHISH_VERSION/gophish-v$GOPHISH_VERSION-linux-64bit.zip
unzip gophish-v$GOPHISH_VERSION-linux-64bit.zip -d $GOPHISH_DIR
sed -i 's/127.0.0.1/0.0.0.0/g' $GOPHISH_DIR/config.json
cat $GOPHISH_DIR/config.json
openssl req -newkey rsa:2048 -nodes -keyout $GOPHISH_DIR/gophish_admin.key -x509 -days 365 -out $GOPHISH_DIR/gophish_admin.crt -batch -subj "/CN=gophish.example.com"
sudo $GOPHISH_DIR/gophish