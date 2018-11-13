FROM forseti/forseti:latest

RUN pip install google-cloud-pubsub

COPY app/* /app/
WORKDIR /app

CMD ["python","-u","-m","/app/worker"]
