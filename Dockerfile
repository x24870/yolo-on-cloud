# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# only copy mlserver to container
# TODO: remove unused modules in requirments.txt
COPY mlserver /code/
ENTRYPOINT ["python", "mlserver/mlserverclient.py"]
