# syntax=docker/dockerfile:1

FROM python

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .
