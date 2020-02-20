## Installation

Abaddon can be installed by launching theses commands


```sh
git clone git@bitbucket.org:Ibrahimous/abaddon.git
cd abaddon
bash setup/install.sh
```

Note that this script will also start Abaddon

This software has been tested on : 

`Linux Kali 4.16.0-kali2-amd64 #1 SMP Debian 4.16.12-1kali1 (2018-05-28) x86_64 GNU/Linux`

## Manual setup

### Install Django

```sh
sudo aptitude install python3-pip python3-django -ry
sudo pip3 install django
```

N.B. : with python3 and django, creating a project is done like this:

python3 -m django startproject abaddon

### Install postgresql

For a PostgreSQL installation tutorial, see for instance that [link][doc], which consists roughly in doing just that:

```sh
$ sudo aptitude install postgresql postgresql-client pgadmin3 -ry
```

Postgres starts automatically on Debian, not on Kali for some reason. You might have to type:
```sh
$ sudo /etc/init.d/postgresql start
```

Then, do:

```sh
$ sudo su -
# su - postgres
postgres@Kali:~$ createuser -P -s -e red-teamer
Saisir le mot de passe pour le nouveau rôle :
Le saisir de nouveau :
CREATE ROLE "red-teamer" PASSWORD 'md55...93' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;
postgres@Kali:~$ createdb abaddondb
```

### Other dependencies from Patrowl ?

```sh
sudo apt install build-essential python2.7-dev git curl rabbitmq-server postgresql
```

### Install postgre dependencies for django

```sh
sudo aptitude install python-psycopg2 libpq-dev -ry
sudo pip3 install psycopg2
```

Now you may fill the settings.py file wih something like:

```
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'abaddondb',                      
        'USER': 'red-teamer',
        'PASSWORD': 'xxx',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
```

### Install django-bootstrap4

```sh
$ sudo pip3 install django-bootstrap4 => NO
```

### Install django-adminlte

```sh
sudo pip3 install django-adminlte2
```

### Install celery

```sh
$ sudo pip3 install celery
```

=> Successfully installed celery billiard kombu amqp vine

### Install events, jsonfield django-celery-beat

```sh
$ sudo pip3 install events
$ sudo pip3 install jsonfield
$ sudo pip3 install django-celery-beat
```

### Known problems

```sh
$ sudo apt-get remove python3-pip; sudo apt-get install python3-pip
$ sudo pip3 install Django --upgrade
```
If you get a "pip3 command not found" error:
`$ sudo apt-get remove python3-pip; sudo apt-get install python3-pip`

If Nmap scan refuse to works proprely

- install nmaptocsv

`sudo pip install nmaptocsv`

- Run syncdb to Fix the NMAP bug.

`python3 manage.py migrate --run-syncdb`


## Create project

```sh
$ python3 -m django startproject abaddon
$ python3 manage.py runserver
```

## Load data

`python3 manage.py loaddata var/data/assets.AssetCategory.json # ==> the only one working`

KO:

```sh
python3 manage.py loaddata var/data/engines.Engine.json
python3 manage.py loaddata var/data/engines.EnginePolicyScope.json
python3 manage.py loaddata var/data/engines.EnginePolicy.json
```

## TODO

1. That doc sucks - add requirements etc

### Install AWS tools

```
sudo pip3 install awscli boto3 -U --ignore-installed six
...
Successfully installed awscli boto3 six PyYAML botocore rsa colorama docutils s3transfer jmespath python-dateutil urllib3 pyasn1
Cleaning up...

Create user with Amazon[EC2|S3|CloudFrontDirectory]FullAccess

Using the credentials obtained, configure AWS:

$ aws configure
AWS Access Key ID [None]: ...
AWS Secret Access Key [None]: ...
Default region name [None]: eu-west-3
Default output format [None]: text
```

#### Configure SSM

WORKS with SSM activated => you need to: create a role, create an activation, and associate the IAM role to your EC2 instance 
 => https://stackoverflow.com/questions/47034797/invalidinstanceid-an-error-occurred-invalidinstanceid-when-calling-the-sendco/47036168#47036168?newreg=1bc535995fec49919b21385cd096935a


2. AWS interaction - 

# References

https://github.com/adamcharnock/django-adminlte2
http://django-adminlte2.readthedocs.io/en/latest/quickstart.html
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html & https://linuxacademy.com/howtoguides/posts/show/topic/14209-automating-aws-with-python-and-boto3
# INSTALL.md

## Testing environnement

`Linux Kali 4.16.0-kali2-amd64 #1 SMP Debian 4.16.12-1kali1 (2018-05-28) x86_64 GNU/Linux`

## Requirements

### Install Django

```sh
sudo aptitude install python3-pip python3-django -ry
sudo pip3 install django
```

N.B. : with python3 and django, creating a project is done like this:

python3 -m django startproject abaddon

### Install postgresql

For a PostgreSQL installation tutorial, see for instance that [link][doc], which consists roughly in doing just that:

```sh
$ sudo aptitude install postgresql postgresql-client pgadmin3 -ry
```

Postgres starts automatically on Debian, not on Kali for some reason. You might have to type:
```sh
$ sudo /etc/init.d/postgresql start
```

Then, do:

```sh
$ sudo su -
# su - postgres
postgres@Kali:~$ createuser -P -s -e red-teamer
Saisir le mot de passe pour le nouveau rôle :
Le saisir de nouveau :
CREATE ROLE "red-teamer" PASSWORD 'md55...93' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;
postgres@Kali:~$ createdb abaddondb
```

### Other dependencies from Patrowl ?

```sh
sudo apt install build-essential python2.7-dev git curl rabbitmq-server postgresql
```

### Install postgre dependencies for django

```sh
sudo aptitude install python-psycopg2 libpq-dev -ry
sudo pip3 install psycopg2
```

Now you may fill the settings.py file wih something like:

```
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'abaddondb',                      
        'USER': 'red-teamer',
        'PASSWORD': 'xxx',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
```

### Install django-bootstrap4

```sh
$ sudo pip3 install django-bootstrap4 => NO
```

### Install django-adminlte

```sh
sudo pip3 install django-adminlte2
```

### Install celery

```sh
$ sudo pip3 install celery
```

=> Successfully installed celery billiard kombu amqp vine

### Install events, jsonfield django-celery-beat

```sh
$ sudo pip3 install events
$ sudo pip3 install jsonfield
$ sudo pip3 install django-celery-beat
```

### Known problems

```sh
$ sudo apt-get remove python3-pip; sudo apt-get install python3-pip
$ sudo pip3 install Django --upgrade
```
If you get a "pip3 command not found" error:
`$ sudo apt-get remove python3-pip; sudo apt-get install python3-pip`

##### Nmap scan refuse to works proprely

- install nmaptocsv

`sudo pip install nmaptocsv`

- Run syncdb to Fix the NMAP bug.

`python3 manage.py migrate --run-syncdb`


## Create project

```sh
$ python3 -m django startproject abaddon
$ python3 manage.py runserver
```

## Load data

`python3 manage.py loaddata var/data/assets.AssetCategory.json # ==> the only one working`

KO:

```sh
python3 manage.py loaddata var/data/engines.Engine.json
python3 manage.py loaddata var/data/engines.EnginePolicyScope.json
python3 manage.py loaddata var/data/engines.EnginePolicy.json
```

## TODO

1. That doc sucks - add requirements etc

### Install AWS things

```
sudo pip3 install awscli boto3 -U --ignore-installed six
...
Successfully installed awscli boto3 six PyYAML botocore rsa colorama docutils s3transfer jmespath python-dateutil urllib3 pyasn1
Cleaning up...

Create user with Amazon[EC2|S3|CloudFrontDirectory]FullAccess

Using the credentials obtained, configure AWS:

$ aws configure
AWS Access Key ID [None]: ...
AWS Secret Access Key [None]: ...
Default region name [None]: eu-west-3
Default output format [None]: text
```

#### Configure SSM

WORKS with SSM activated => you need to: create a role, create an activation, and associate the IAM role to your EC2 instance 
 => https://stackoverflow.com/questions/47034797/invalidinstanceid-an-error-occurred-invalidinstanceid-when-calling-the-sendco/47036168#47036168?newreg=1bc535995fec49919b21385cd096935a


2. AWS interaction - 

# References

https://github.com/adamcharnock/django-adminlte2
http://django-adminlte2.readthedocs.io/en/latest/quickstart.html
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html & https://linuxacademy.com/howtoguides/posts/show/topic/14209-automating-aws-with-python-and-boto3

