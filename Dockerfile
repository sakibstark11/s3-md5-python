FROM debian:bullseye-slim

RUN apt update
RUN apt install python3 -y

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "bash -c '$1'" ]
