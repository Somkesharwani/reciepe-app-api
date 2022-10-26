FROM python:3.9-alpine3.13
LABEL maintainer="test.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirement.txt /tmp/requirement.txt
COPY ./requirement.dev.txt /tmp/requirement.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV= false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install tk &&\
    apk add tk && \
    apk add --update postgresql-client jpeg-dev && \
    apk add --update --virtual .tmp-build-deps \
      build-base postgresql-dev musl-dev zlib-dev && \
    /py/bin/pip install -r /tmp/requirement.txt && \
    if  [ $DEV = "true" ] ; \
       then /py/bin/pip install -r /tmp/requirement.dev.txt ; \
       echo "This script runing in DEV mode" ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

ENV PATH="/py/bin:$PATH"

USER django-user
