FROM nginx:latest

# Dockerfile metadata
MAINTAINER Crypt0-M3lon
LABEL version="1.0"
LABEL description="Dockerfile base RedELK"

# docker hardcoded sh...
SHELL ["/bin/bash", "-c"]


ADD default /etc/nginx/conf.d/default.conf
 
# Give execution rights on the cron job
RUN chmod 0644 /etc/nginx/conf.d/default.conf
 
