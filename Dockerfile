FROM alpine:3.6

RUN  apk add --no-cache --update bash && \
     apk add python py-pip gcc python-dev build-base g++ musl-dev tar ca-certificates openssl && \
     pip install --upgrade pip

ADD . /PERMIANJOBS

WORKDIR /PERMIANJOBS

RUN apk add python-dev curl libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev

RUN pip install -r requirements.txt

CMD ["/bin/bash", "-c", "source arguments.env && python jobMAIN.py"]
