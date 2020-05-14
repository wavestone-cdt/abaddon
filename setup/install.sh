#!/bin/bash
set -e

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
abaddonPATH="$(dirname "$SCRIPTPATH")"

echo -e "\n\nADDING PACKAGES\n\n"
sudo bash -c "echo 'deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main' > /etc/apt/sources.list.d/pgdg.list"
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo bash -c "echo 'deb https://download.docker.com/linux/debian stretch stable' > /etc/apt/sources.list.d/docker.list"
sudo apt-get install wget ca-certificates -y
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add

echo -e "\n\nUPGRADING OS\n\n"
sudo apt-get update
sudo apt-get install -y aptitude
sudo apt-get install -y software-properties-common
sudo apt-get upgrade -y

echo -e "\n\nINSTALLING POSTGRESQL AND DOCKER\n\n"
sudo aptitude install postgresql postgresql-client pgadmin3 build-essential python2.7-dev git curl rabbitmq-server python-psycopg2 libpq-dev recon-ng -ry
sudo /etc/init.d/postgresql start
sudo apt-get remove docker docker-engine docker.io -y
sudo aptitude install docker-ce docker-ce-cli containerd.io docker-compose -ry
sudo groupadd -f docker
sudo chown root:docker /var/run/docker.sock
sudo usermod -a -G docker "$(whoami)"
sudo systemctl restart docker

echo -e "CREATING DB & USER\n\n"
sudo su postgres -c "createuser -P -s -e red-teamer" || true
sudo su postgres -c "createdb abaddondb" || true

echo -e "INSTALLING PYTHON MODULES\n\n"
sudo apt-get remove python3-pip -y
sudo apt-get install python3-pip -y

#Python dependencies
pip3 install -r $SCRIPTPATH/requirements.txt

if [ ! -d $abaddonPATH/nmaptocsv ]
then
    git clone https://github.com/maaaaz/nmaptocsv.git $abaddonPATH/nmaptocsv
else
    pushd $abaddonPATH/nmaptocsv
    git pull
    popd
fi
sudo cp $abaddonPATH/nmaptocsv/nmaptocsv.py /usr/local/bin/nmaptocsv

echo -e "\n\nPATCHING SIX\n\n"
#Patch one dependencie, and add ~/.local/bin to PATH
sed -i 's/django.utils.six/six/g' $(python3 -m site --user-site)/datetimewidget/widgets.py
echo -e "export PATH=\$PATH:~/.local/bin" >> ~/.bashrc
#Other dependencies

echo -e "\n\nRESTARTING RABBIT-MQ\n\n"
sudo service rabbitmq-server start

echo -e "\n\nAPPLYING DJANGO MIGRATIONS AND CREATING A NEW USER\n\n"
python3 $abaddonPATH/manage.py makemigrations
python3 $abaddonPATH/manage.py migrate
python3 $abaddonPATH/manage.py createsuperuser

newgrp docker
