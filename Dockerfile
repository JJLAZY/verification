FROM python

WORKDIR /code

ADD . /code

RUN pip install gunicorn
RUN pip install sanic
RUN pip install numpy
RUN pip install requests
RUN pip install pillow
RUN pip install sklearn
RUN pip install pyzbar

EXPOSE 8007

CMD gunicorn  -w 4 app:app --bind 0.0.0.0:8007 --worker-class sanic.worker.GunicornWorker