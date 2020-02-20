#!/bin/bash 

sudo /etc/init.d/postgresql restart
sudo systemctl restart docker
sudo service rabbitmq-server restart
(celery -A abaddon worker -l info & python3 manage.py runserver 8000)

