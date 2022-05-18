import requests
import csv
import re
import time
from datetime import datetime
import os

inspectorSample = {
    "apiVersion": 'lazykoala.isala.me/v1alpha1',
    "kind": 'Inspector',
    "namespace": 'lazy-koala',
    "metadata": {
        "name": 'sample',
    },
    "spec": {
        "deploymentRef": "",
        "serviceRef": "",
        "modelName": "",
        "namespace": "default"
    },
};

with open('usage_data.csv', 'w') as f:
    f.write("time,name,cpu,memory\n")



def pool_metrics():
    print(f"{datetime.now()}: Pooling metrics...")
    r = requests.get("http://127.0.0.1:8001/apis/metrics.k8s.io/v1beta1/namespaces/lazy-koala/pods")
    data = []
    for item in r.json()['items']:
        cpu = 0
        memory = 0
        for container in item['containers']:
            cpu +=  int(re.sub('\D', '', container['usage']['cpu']))
            memory += int(re.sub('\D', '', container['usage']['memory']))

        data.append({
            'time': int(time.time()),
            'name': item['metadata']['name'],
            'cpu': cpu / 1000 / 1000,
            'memory': memory / 1000,
        })
    data[1]['cpu'] += data[0]['cpu']
    data[1]['memory'] += data[0]['memory']
    data.pop(0)
    
    with open('usage_data.csv', 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['time', 'name', 'cpu', 'memory'])
        writer.writerows(data)


for i in range(11):

    if i == 0:
        pool_metrics()
        time.sleep(10)
        continue
    
    print(f"{datetime.now()}: Deploying inspector service-{i} ")

    inspectorSample['metadata']['name'] = f"service-{i}-278a24d6"
    inspectorSample['spec']['deploymentRef'] = f"service-{i}-278a24d6"
    inspectorSample['spec']['serviceRef'] = f"service-{i}-278a24d6"
    inspectorSample['spec']['modelName'] = f"service-{i}-278a24d6"

    r = requests.post("http://127.0.0.1:8001/apis/lazykoala.isala.me/v1alpha1/namespaces/default/inspectors/", json=inspectorSample)

    print(f"{datetime.now()}: Sleeping for 5 minutes...")

    os.system("kubectl delete pods -n lazy-koala --all")

    time.sleep((60 * 10))

    pool_metrics()