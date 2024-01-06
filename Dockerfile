FROM python:3.9 

WORKDIR /app

ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ADD . /app

ENTRYPOINT ["python", "name-match-cmd.py"]
