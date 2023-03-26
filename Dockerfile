FROM debian:bullseye-slim

RUN apt update
RUN apt install python3 -y

COPY ./ /
ARG command

ENTRYPOINT [ "/bin/sh", "-c", "$command" ]
