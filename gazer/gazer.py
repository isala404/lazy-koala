import os
import threading
import time
import termplotlib as tpl
import pandas as pd
from bcc import BPF
from socket import inet_ntop, AF_INET
from struct import pack
from config import config_watcher
import requests
from prometheus_client import Histogram, Counter, Gauge
import re

ms = Histogram("request_duration_seconds", "TCP event latency", ["namespace", "serviceName", "podName"])
tx_kb = Histogram("transmitted_bytes", "Number of sent bytes during TCP event", ["namespace", "serviceName", "podName"])
rx_kb = Histogram("acknowledged_bytes", "Number of received bytes during TCP event",
                  ["namespace", "serviceName", "podName"])
request_sent = Counter("requests_sent", "Total request sent", ["namespace", "serviceName", "podName"])
request_received = Counter("requests_received", "Total request received", ["namespace", "serviceName", "podName"])
backlog = Gauge("backlog", "Request backlog", ["namespace", "serviceName", "podName", "level"])
cpu = Gauge("cpu_seconds", "CPU usage", ["namespace", "serviceName", "podName"])
memory = Gauge("memory_usage_bytes", "Memory usage", ["namespace", "serviceName", "podName"])
request_exchanges = Counter("request_exchanges", "Request exchanges between services", ["origin", "destination"])


class Gazer:
    request_df = pd.DataFrame(columns=["PID", "COMM", "LADDR", "LPORT", "RADDR", "RPORT", "TX_KB", "RX_KB", "MS"])
    syn_df = pd.DataFrame(columns=["backlog", "slot", "saddr", "lport", "value", "outdated"])
    bpf_text = ""
    console_mode = False
    kube_api = os.getenv("KUBERNETES_SERVICE_HOST", "localhost:8001")
    kube_token = ""

    def __init__(self, console_mode=False):
        self.console_mode = console_mode
        with open('bpf.c', 'r') as f:
            bpf_text = f.read()

        with open('sock_state.c', 'r') as f:
            bpf_text += f.read()

        with open('syn_backlog.c', 'r') as f:
            bpf_text += f.read()

        try:
            with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as f:
                self.kube_token = f.read()
        except FileNotFoundError:
            print("Kube token was not set")

        bpf_text = bpf_text.replace('FILTER_PID', '')
        self.bpf_text = bpf_text.replace('ADDRFILTER', '')
        self.b = BPF(text=self.bpf_text)
        self.b["ipv4_events"].open_perf_buffer(self.ipv4_request_event, page_cnt=64)
        self.syn_backlog_buffer = self.b['syn_backlog']

    def ipv4_request_event(self, cpu, data, size):
        event = self.b['ipv4_events'].event(data)
        event = {
            "PID": event.pid,
            "COMM": event.task.decode('utf-8', 'replace'),
            "LADDR": inet_ntop(AF_INET, pack("I", event.saddr)),
            "LPORT": event.ports >> 32,
            "RADDR": inet_ntop(AF_INET, pack("I", event.daddr)),
            "RPORT": event.ports & 0xffffffff,
            "TX_KB": float(event.tx_b),
            "RX_KB": float(event.rx_b),
            "MS": float(event.span_us) / 1000,
        }

        # Write to prometheus
        if event['LADDR'] in config_watcher.config:
            pod = config_watcher.config[event['LADDR']]

            if event['RADDR'] in config_watcher.config:
                rpod = config_watcher.config[event['RADDR']]
                if not rpod['isService']:
                    return
                request_received.labels(rpod['namespace'], rpod['serviceName'], rpod['name']).inc()
                request_exchanges.labels(pod['serviceName'], rpod['serviceName']).inc()

            ms.labels(pod['namespace'], pod['serviceName'], pod['name']).observe(event['MS'] / 1000000)
            tx_kb.labels(pod['namespace'], pod['serviceName'], pod['name']).observe(event['TX_KB'])
            rx_kb.labels(pod['namespace'], pod['serviceName'], pod['name']).observe(event['RX_KB'])
            request_sent.labels(pod['namespace'], pod['serviceName'], pod['name']).inc()

            if self.console_mode:
                self.request_df = self.request_df.append(event, ignore_index=True)
                self.request_df = self.request_df[-10:]

    def poll_requests(self):
        while True:
            self.b.perf_buffer_poll()

    def poll_kube_api(self):
        while True:
            for pod in config_watcher.config.values():
                try:
                    if pod['isService']:
                        continue
                    cpu_usage = 0
                    memory_usage = 0
                    r = requests.get(
                        f"https://{self.kube_api}/apis/metrics.k8s.io/v1beta1/namespaces/{pod['namespace']}/pods/{pod['name']}",
                        headers={"Authorization": f"Bearer {self.kube_token}"}, verify=False)
                    data = r.json()
                    for container in data['containers']:
                        cpu_usage += int(re.sub('\D', '', container['usage']['cpu']))
                        memory_usage += int(re.sub('\D', '', container['usage']['memory'])) * 1024

                    # Write to prometheus
                    cpu.labels(pod['namespace'], pod['serviceName'], pod['name']).set(cpu_usage)
                    memory.labels(pod['namespace'], pod['serviceName'], pod['name']).set(memory_usage)
                except Exception as e:
                    print(e)
            time.sleep(40)

    def poll_syn_backlog(self):
        while True:
            try:
                data = self.syn_backlog_buffer.items()
                
                self.syn_df["outdated"] = True
                backlog.clear()

                for pod in config_watcher.config.values():
                    if pod['isService']:
                        continue
                    backlog.labels(pod['namespace'], pod['serviceName'], pod['name'], 1).set(0)
                    backlog.labels(pod['namespace'], pod['serviceName'], pod['name'], 2).set(0)

                for row in data:
                    saddr = inet_ntop(AF_INET, pack("I", row[0].saddr))

                    # Write to prometheus
                    if saddr in config_watcher.config:
                        pod = config_watcher.config[saddr]

                        backlog.labels(pod['namespace'], pod['serviceName'], pod['name'], int(row[0].slot)).set(
                            int(row[1].value))

                        if self.console_mode:
                            self.syn_df = self.syn_df.append({
                                "backlog": row[0].backlog,
                                "slot": row[0].slot,
                                "saddr": inet_ntop(AF_INET, pack("I", row[0].saddr)),
                                "lport": row[0].lport,
                                "value": row[1].value,
                                "outdated": False,
                            }, ignore_index=True)
                self.syn_backlog_buffer.clear()
            except Exception as e:
                print(e)
            time.sleep(5)

    def syn_backlog_text(self):
        self.syn_df['saddr_port'] = self.syn_df["saddr"] + ":" + self.syn_df["lport"].astype(str)
        grouped_df = self.syn_df.groupby('saddr_port')
        out = "SYN Backlog\n"
        for key, item in grouped_df:
            x, y = [], []
            out += f"\n{key}\n"
            df = grouped_df.get_group(key)
            new_data = df.loc[df['outdated'] == False]

            if new_data.empty:
                x.append(0)
                y.append("0-1")
            else:
                for entry in new_data.sort_values(by=['slot']).to_dict('records'):
                    x.append(entry['value'])
                    y.append(f"{entry['slot'] - 1} -> {entry['slot']}")
            fig = tpl.figure()
            fig.barh(x, y, force_ascii=True)
            out += fig.get_string() + "\n"
        return out

    def request_log_text(self):
        if self.request_df.empty:
            return ""
        return self.request_df.tail(10).__str__()

    def poll_data_in_bg(self):
        poll_syn_backlog = threading.Thread(target=self.poll_syn_backlog, args=())
        poll_syn_backlog.daemon = True
        poll_syn_backlog.start()

        poll_requests = threading.Thread(target=self.poll_requests, args=())
        poll_requests.daemon = True
        poll_requests.start()

        poll_kube_api = threading.Thread(target=self.poll_kube_api, args=())
        poll_kube_api.daemon = True
        poll_kube_api.start()

        if not self.console_mode:
            poll_syn_backlog.join()
            poll_requests.join()
            poll_kube_api.join()
