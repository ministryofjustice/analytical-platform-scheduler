FROM python:3.11-slim-bullseye
RUN apt-get update && apt-get install -y pkg-config
COPY requirements.txt .
COPY scheduler.py app.py
RUN pip3 install -r requirements.txt

CMD gunicorn -w 1 -b 0.0.0.0:5000 'app:app'
