FROM python:3.9-alpine3.13
LABEL maintainer="test.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirement.txt /tmp/requirement.txt
COPY ./requirement.dev.txt /tmp/requirement.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \ 
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirement.txt && \
    if  [ $DEV =='true'];\
       then /py/bin/pip install -r /tmp/requirement.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        djanngo-user

ENV PATH="/py/bin:$PATH"

USER  django-user

