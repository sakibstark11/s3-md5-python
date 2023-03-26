FROM debian:bullseye-slim

RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y

COPY ./dev-requirements.txt /
RUN pip install dev-requirements.txt

CMD [ "" ]
