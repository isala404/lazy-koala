FROM alpine:edge

RUN apk add bcc-tools py3-pip py3-numpy py3-pandas

RUN pip install termplotlib

WORKDIR /gazer

COPY . .

CMD ["python3", "main.py"]