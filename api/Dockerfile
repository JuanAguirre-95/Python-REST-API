FROM python:3.8.5-buster
 
EXPOSE 5000 

RUN apt-get update
RUN apt-get install -y python3 uwsgi nano nginx bash
RUN pip install --upgrade pip

COPY requirements.txt /home/

RUN pip install -r /home/requirements.txt

WORKDIR /home/

COPY . .

WORKDIR /home/API

ENTRYPOINT ["python"]

CMD ["app.py"]
