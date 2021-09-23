# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python

COPY requirements.txt ./
RUN pip install -r requirements.txt

# only copy mlserver to container
# TODO: remove unused modules in requirments.txt
COPY ./mlserver .
ENTRYPOINT ["python", "./mlserverclient.py"]
