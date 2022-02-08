FROM alpine:3.15

RUN apk add bcc-tools py3-pip py3-numpy py3-pandas py3-bcc

RUN pip install termplotlib pyinotify pyyaml prometheus_client

WORKDIR /gazer

COPY . .

CMD ["python3", "main.py"]