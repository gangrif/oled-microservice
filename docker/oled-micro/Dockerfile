FROM resin/rpi-raspbian:jessie

RUN apt-get update --fix-missing
RUN apt-get install python-pip


RUN pip install flask flask-jsonpify flask-restful

RUN mkdir /service

COPY ../../ledfun.py /service/
COPY ../../oledtest.py /service/
COPY ../../main.py /service/



EXPOSE 5002 

CMD ["/service/main.py"]

