#!/bin/bash
#TODO: obfuscate & minify this script

HOME_EC2="/home/ec2-user"
GOPHISH_DIR="$HOME_EC2/Gophish"
GOPHISH_VERSION="0.7.1"

# Create a directory to store Gophish
mkdir -p $GOPHISH_DIR

# Getting some dependancies installed
#sudo yum update -y
#sudo yum install golang-go unzip git -y

# Pulling down goPhish, unpacking and configuring goPhish
cd $GOPHISH_DIR
wget https://github.com/gophish/gophish/releases/download/$GOPHISH_VERSION/gophish-v$GOPHISH_VERSION-linux-64bit.zip
unzip gophish-v$GOPHISH_VERSION-linux-64bit.zip -d $GOPHISH_DIR
#ln -s $GOPHISH_DIR/gophish-v$GOPHISH_VERSION-linux-64bit/ $GOPHISH_DIR

sed -i 's/127.0.0.1/0.0.0.0/g' $GOPHISH_DIR/config.json
cat $GOPHISH_DIR/config.json

#chmod +x $GOPHISH_DIR/gophish

# Creating a SSL Cert
# TODO: do that with certbot
openssl req -newkey rsa:2048 -nodes -keyout $GOPHISH_DIR/gophish_admin.key -x509 -days 365 -out $GOPHISH_DIR/gophish_admin.crt -batch -subj "/CN=gophish.example.com"

# Configuring  goPhish to run as a service
#sudo cp gophish.service /lib/systemd/system/gophish.service
#sudo cp gophish.sh /root/gophish.sh
#sudo chmod +x /root/gophish.sh
#sudo systemctl daemon-reload
#sudo systemctl start gophish

sudo $GOPHISH_DIR/gophish