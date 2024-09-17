FROM python:3.12

WORKDIR blockchain-listener

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]
