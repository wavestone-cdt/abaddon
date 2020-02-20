FROM ubuntu:latest

# Dockerfile metadata
MAINTAINER Crypt0-M3lon
LABEL version="1.0"
LABEL description="Dockerfile base RedELK"

# docker hardcoded sh...
SHELL ["/bin/bash", "-c"]


RUN apt update && apt install -y cron curl rsyslog
RUN apt install -y python3-pil python3-pip
RUN pip3 install elasticsearch requests

# Add crontab file in the cron directory
ADD cron.d/redelk /etc/cron.d/redelk
 
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/redelk
 
ADD scripts/ /usr/share/redelk/bin/
RUN chmod -R 775 /usr/share/redelk/bin/*

ADD etc/redelk/ /etc/redelk/

RUN mkdir -p /var/log/redelk 

# set entry point
WORKDIR "/opt/redelk"
COPY launcher.sh /opt/redelk/
RUN chmod +x launcher.sh
ENTRYPOINT ["./launcher.sh"]

