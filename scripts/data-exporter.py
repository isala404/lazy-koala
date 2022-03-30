from flask import Flask, request, jsonify
from datetime import datetime
import pymongo
import os

app = Flask(__name__)


myclient = pymongo.MongoClient(os.getenv("MONGODB_URI"))
mydb = myclient["metrics"]


@app.route('/save', methods=['GET', 'POST'])
def add_message():
    content = request.json
    mycol = mydb[content['service']]
    x = mycol.insert_one({"data": content['data'], "time": datetime.now()})
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)







# import grequests
# import urllib.parse
# import numpy as np

# services = [
#     "service-1-18f76028",
#     "service-10-18f76028",
#     "service-2-18f76028",
#     "service-3-18f76028",
#     "service-4-18f76028",
#     "service-5-18f76028",
#     "service-6-18f76028",
#     "service-7-18f76028",
#     "service-8-18f76028",
#     "service-9-18f76028",
# ]

# samples = ["1m", "5m", "15m"]

# metrics = [
#        'rate(requests_sent_total{serviceName="SERVICE_NAME"}[SAMPLE])',
#        'sum by (serviceName) (rate(requests_received_total{serviceName="SERVICE_NAME"}[SAMPLE]))',
#        'rate(request_duration_seconds_sum{serviceName="SERVICE_NAME"}[SAMPLE])',
#        'avg_over_time(cpu_seconds{serviceName="SERVICE_NAME"}[SAMPLE])',
#        'avg_over_time(memory_usage_bytes{serviceName="SERVICE_NAME"}[SAMPLE])',
#        'rate(acknowledged_bytes_sum{serviceName="SERVICE_NAME"}[SAMPLE])',
#        'rate(transmitted_bytes_sum{serviceName="SERVICE_NAME"}[SAMPLE])',
#        'avg_over_time(backlog{level="1",serviceName="SERVICE_NAME"}[SAMPLE])',
#        'sum by (serviceName) (avg_over_time(backlog{level!="1",serviceName="SERVICE_NAME"}[SAMPLE]))',
# ]

# requests = []

# def chunks(l, n):
#     n = max(1, n)
#     return (l[i:i+n] for i in range(0, len(l), n))

# for service in services:
#     for sample in samples:
#         for metric in metrics:
#             query = metric.replace("SERVICE_NAME", service).replace("SAMPLE", sample)
#             url = "http://127.0.0.1:9090/api/v1/query?query="+urllib.parse.quote_plus(query)
#             requests.append(grequests.get(url))
#     respon =  grequests.map(requests)
#     f
#     break;
