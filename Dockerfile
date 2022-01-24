FROM node:12-buster

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y wget
RUN apt-get install -y git


RUN mkdir /TaxHub
WORKDIR /TaxHub
COPY requirements.txt /TaxHub/
COPY requirements-common.txt /TaxHub/
RUN pip3 install -r requirements.txt
COPY . /TaxHub
RUN cd static && npm ci
RUN cd -
ENTRYPOINT ["sh", "entrypoint.sh"]
EXPOSE 80