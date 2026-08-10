FROM python:3.13-slim
WORKDIR /app
COPY python /app/python
COPY examples/python-integration /app/service
RUN pip install /app/python uvicorn
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8081"]
