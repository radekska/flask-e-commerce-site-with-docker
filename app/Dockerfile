FROM python

WORKDIR /main

COPY requirements.txt .

RUN apt-get update && apt-get dist-upgrade

RUN pip install -r requirements.txt

COPY src .

EXPOSE 8000

CMD ["python", "app.py"]