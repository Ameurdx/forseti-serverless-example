FROM python:slim-stretch

RUN pip install google-cloud-pubsub

COPY job_publisher.py /app

CMD ["python","-u","/app/job_publisher.py"]
