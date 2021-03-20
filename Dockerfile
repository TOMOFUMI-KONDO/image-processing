FROM tensorflow/tensorflow:1.14.0-py3

RUN mkdir -p /var/app
WORKDIR /var/app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    opencv-python \
    opencv-contrib-python && \
    apt-get update && apt-get install -y libgl1-mesa-dev

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

RUN apt-get install -y nginx

RUN mkdir -p ./src
COPY src ./src
COPY uwsgi ./uwsgi
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY app.py ./
COPY startup.sh ./

CMD ["/bin/bash", "/var/app/startup.sh"]