FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install -r requirements.txt

COPY . .
