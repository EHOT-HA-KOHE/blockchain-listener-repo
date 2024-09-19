FROM python:3.12-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

CMD ["python", "main.py"]
