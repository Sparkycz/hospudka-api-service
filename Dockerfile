FROM alpine:3.7

WORKDIR /app

RUN apk add --update --no-cache python3 uwsgi-python3

RUN pip3 install --upgrade pip

# install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# load app into image
COPY http_server.py .
COPY hospudka hospudka

ENTRYPOINT [ \
    "uwsgi", \
    "--plugins=python3", \
    "--master", \
    "--workers=4", \
    "--threads=50", \
    "--listen=100", \
    "--http11-socket=:8080", \
    "--chdir=/app", \
    "--buffer-size=32768", \
    "--env=CONFIG=/app/hospudka/config/development.py", \
    "--module=hospudka.app:create_app()" \
]
