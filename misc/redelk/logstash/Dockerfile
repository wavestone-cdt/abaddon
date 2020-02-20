ARG ELK_VERSION

# https://github.com/elastic/logstash-docker
FROM docker.elastic.co/logstash/logstash:${ELK_VERSION}

SHELL ["/bin/bash", "-c"]
RUN mkdir -p /usr/share/logstash/GeoLite2-dbs 
# RUN curl http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz -o /tmp/GeoLite2-City.tar.gz 
# RUN curl http://geolite.maxmind.com/download/geoip/database/GeoLite2-ASN.tar.gz -o /tmp/GeoLite2-ASN.tar.gz
# RUN tar zxvf /tmp/GeoLite2-ASN.tar.gz 
# RUN tar zxvf /tmp/GeoLite2-City.tar.gz 
# RUN mv Geo*/*.mmdb /usr/share/logstash/GeoLite2-dbs 
# RUN chown -R 1000:1000 /usr/share/logstash/GeoLite2-dbs 

# Add your logstash plugins setup here
# Example: RUN logstash-plugin install logstash-filter-json
