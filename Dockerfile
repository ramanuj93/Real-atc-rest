from python:3.7-buster

RUN pip install --upgrade pip \
    && apt-get -y update \
    && apt-get -y install libasound2 \
    && apt-get -y install libsndfile1-dev \
    && apt-get -y install ffmpeg


WORKDIR /app

COPY . /app

RUN pip --no-cache-dir install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]

CMD ["app.py"]