# checkov:skip=CKV_DOCKER_2: Migrate as is
# checkov:skip=CKV_DOCKER_3: Migrate as is

FROM python:3.11-slim-bullseye
RUN apt-get update && apt-get install -y pkg-config
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY scheduler.py app.py
COPY static static
COPY templates templates

CMD gunicorn -w 1 -b 0.0.0.0:5000 'app:app'
