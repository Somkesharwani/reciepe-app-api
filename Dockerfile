FROM python:3.9-alpine3.13
LABEL maintainer="test.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirement.txt /tmp/requirement.txt
COPY ./requirement.dev.txt /tmp/requirement.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV= false
RUN echo $DEV
RUN more /tmp/requirement.dev.txt
RUN python -m venv /py && \ 
    /py/bin/pip install --upgrade pip && \
    apk add --update postgresql-client && \
    apk add --update --virtual .tmp-build-deps \
      build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirement.txt && \
    #/py/bin/pip install -r /tmp/requirement.dev.txt ; \
    if  [ $DEV = "true" ] ; \
       then \
       /py/bin/pip install -r /tmp/requirement.dev.txt ; \
       echo "This script runing in DEV mode" ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"

USER  django-user

