FROM python:3.9-buster

RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/rekome
WORKDIR /opt/app
COPY requirements.txt start-server.sh /opt/app/
RUN pip install -r requirements.txt

COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log
COPY src /opt/app/rekome/
RUN chown -R www-data:www-data /opt/app
RUN chmod 755 start-server.sh

EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]
