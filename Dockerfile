FROM python:3
RUN mkdir /api
RUN mkdir -p /var/www/learning.nss.team
WORKDIR /api
ADD . /api/
RUN pip install -r requirements.txt
ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh
COPY config/nginx/nginx.conf /etc/nginx/nginx.conf

ENTRYPOINT [ "/entrypoint.sh" ]
