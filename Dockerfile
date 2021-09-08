FROM python:slim

WORKDIR /main

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ .

EXPOSE 8000

CMD ["python", "app.py"]