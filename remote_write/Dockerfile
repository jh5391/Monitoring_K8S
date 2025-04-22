FROM python:3.9-slim
WORKDIR /app
COPY remote_write_example.py .
RUN pip install prometheus_client requests python-snappy
CMD ["python", "remote_write_example.py"]
