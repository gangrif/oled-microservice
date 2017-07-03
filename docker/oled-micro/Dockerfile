FROM resin/rpi-raspbian:jessie

RUN apt-get update --fix-missing
RUN apt-get install python-pip git

RUN pip install flask flask-jsonpify flask-restful
RUN git clone git@github.com:gangrif/oled-microservice.git /service

EXPOSE 5002 

CMD ["/service/main.py"]

