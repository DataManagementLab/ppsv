FROM ubuntu

ENV DJANGO_SETTINGS_MODULE=ppsv.settings_production

RUN apt-get update -y --fix-missing && apt-get upgrade -y
RUN apt-get install -y gcc g++ make python3 python3-dev python3-pip

WORKDIR /seminarplatz
COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8000

WORKDIR /seminarplatz/ppsv
CMD python3 manage.py runserver