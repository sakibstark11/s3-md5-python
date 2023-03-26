FROM debian:bullseye-slim

RUN apt update
RUN apt install python3 -y

COPY ./ /

ENTRYPOINT [ "/bin/sh", "-c" ]
