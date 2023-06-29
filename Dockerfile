# syntax=docker/dockerfile:1

FROM python:3.10
WORKDIR /app
COPY . .
RUN apt update
RUN apt install -y libffi-dev python3-dev ffmpeg
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]
