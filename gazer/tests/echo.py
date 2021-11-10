import time
from flask import Flask, request, Response
import json
import requests

app = Flask('service')


@app.route("/", methods=["POST"])
def handler():
    start_time = time.time()
    try:
        endpoint = request.data.decode()
        if not endpoint:
            endpoint = "https://1.1.1.1"
    except Exception:
        endpoint = "https://1.1.1.1"
    res = requests.get(endpoint)
    duration = time.time() - start_time
    content_size = len(res.content)
    return Response(json.dumps({"endpoint": endpoint, "duration": duration, "content_size": content_size}),
                    mimetype='application/json')


@app.route("/ping", methods=["GET"])
def ping():
    return "pong"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
