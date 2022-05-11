FROM ubuntu:latest

WORKDIR /opt
COPY . .

RUN apt update
RUN apt upgrade -y
RUN apt install -y python3 python3-pip wget

RUN pip install -r requirements.txt

RUN wget https://github.com/caddyserver/caddy/releases/download/v2.5.1/caddy_2.5.1_linux_amd64.tar.gz
RUN tar -xzvf caddy_2.5.1_linux_amd64.tar.gz
RUN rm caddy_2.5.1_linux_amd64.tar.gz

ENTRYPOINT ["sh", "-c", "/opt/heroku_startup.sh"]
