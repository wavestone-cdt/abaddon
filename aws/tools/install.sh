#!/bin/bash
HOME_EC2="/home/ec2-user"
GOPHISH_DIR="$HOME_EC2/Gophish"
#The latest Gophsih version as of 23th December
GOPHISH_VERSION="0.8.0"
mkdir -p $GOPHISH_DIR
cd $GOPHISH_DIR
#https://github.com/gophish/gophish/releases/download/v0.8.0/gophish-v0.8.0-linux-64bit.zip
wget https://github.com/gophish/gophish/releases/download/v$GOPHISH_VERSION/gophish-v$GOPHISH_VERSION-linux-64bit.zip
unzip gophish-v$GOPHISH_VERSION-linux-64bit.zip -d $GOPHISH_DIR
sed -i 's/127.0.0.1/0.0.0.0/g' $GOPHISH_DIR/config.json
cat $GOPHISH_DIR/config.json
openssl req -newkey rsa:2048 -nodes -keyout $GOPHISH_DIR/gophish_admin.key -x509 -days 365 -out $GOPHISH_DIR/gophish_admin.crt -batch -subj "/CN=gophish.example.com"
sudo $GOPHISH_DIR/gophish

#!/bin/bash

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
