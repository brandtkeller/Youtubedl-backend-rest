FROM ubuntu:latest

# These should be overidden at runtime
ENV DB_HOST postgres
ENV DB_NAME postgresdb
ENV DB_USER postgres
ENV DB_PASSWORD postgres123

user root





RUN apt update && ln -fs /usr/share/zoneinfo/America/Los_Angeles /etc/localtime && \
    DEBIAN_FRONTEND=noninteractive apt install -y libpq-dev ffmpeg python3-dev python3-pip && \
    mkdir /data && pip3 install flask Flask-API youtube-dl psycopg2 flask-cors

RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser && \
    chown appuser:appuser /data

USER appuser

WORKDIR /application

COPY *.py /application/

CMD python3 server.py $DB_HOST $DB_NAME $DB_USER $DB_PASSWORD