# syntax=docker/dockerfile:1

FROM python:3.10
WORKDIR /app
COPY requirements.txt requirements.txt
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb
RUN apt install ./wkhtmltox_0.12.6.1-3.bookworm_amd64.deb
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3", "main.py"]
