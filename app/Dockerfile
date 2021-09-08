FROM tensorflow/tensorflow:1.14.0-py3

RUN mkdir -p /var/app
WORKDIR /var/app


RUN apt-get update
RUN apt-get install -y libgl1-mesa-dev curl

# Pythonのパッケージをインストール
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# ホストマシンのモデルファイルを配置
COPY model ./model

# uwsgiの設定ファイルを配置
COPY uwsgi ./uwsgi

# アプリケーションコードを配置
COPY src ./src
COPY app.py .

EXPOSE 8080

CMD ["uwsgi", "--ini", "uwsgi/uwsgi.ini"]