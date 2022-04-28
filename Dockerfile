# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

#File will be created in the root directory
ENV HOME /root
WORKDIR /root

#Copying files over
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

#Port the server is going to be running on
EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait 
RUN chmod +x /wait

#Runs the app
CMD /wait && python3 server.py