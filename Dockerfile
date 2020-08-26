FROM ubuntu:latest

# These should be overidden at runtime
ENV DB_HOST postgres
ENV DB_NAME postgresdb
ENV DB_USER postgres
ENV DB_PASSWORD postgres123

user root

RUN apt install ffmpeg python python3-pip && \
    mkdir /data

RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser && \
    chown appuser:appuser /data

USER appuser

WORKDIR /application

ADD *.py .

RUN pip3 install flask Flask-API youtube-dl psycopg2

CMD python3 server.py $DB_HOST $DB_NAME $DB_USER $DB_PASSWORD