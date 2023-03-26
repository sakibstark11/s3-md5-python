FROM debian:bullseye-slim

RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y

RUN pip install -r dev-requirements.txt

CMD [ "" ]
