import threading
import time
import termplotlib as tpl
import pandas as pd
from bcc import BPF
from socket import inet_ntop, AF_INET
from struct import pack
from config import config_watcher


class Gazer:
    request_df = pd.DataFrame(columns=["PID", "COMM", "LADDR", "LPORT", "RADDR", "RPORT", "TX_KB", "RX_KB", "MS"])
    syn_df = pd.DataFrame(columns=["backlog", "slot", "saddr", "lport", "value", "outdated"])
    bpf_text = ""
    console_mode = False

    def __init__(self, console_mode=False):
        self.console_mode = console_mode
        with open('bpf.c', 'r') as f:
            bpf_text = f.read()

        with open('sock_state.c', 'r') as f:
            bpf_text += f.read()

        with open('syn_backlog.c', 'r') as f:
            bpf_text += f.read()

        bpf_text = bpf_text.replace('FILTER_PID', '')
        self.bpf_text = bpf_text.replace('ADDRFILTER', '')
        self.b = BPF(text=self.bpf_text)
        self.b["ipv4_events"].open_perf_buffer(self.ipv4_request_event, page_cnt=64)
        self.syn_backlog_buffer = self.b['syn_backlog']

    def ipv4_request_event(self, cpu, data, size):
        event = self.b["ipv4_events"].event(data)
        LADDR = inet_ntop(AF_INET, pack("I", event.saddr))
        RADDR = inet_ntop(AF_INET, pack("I", event.daddr))

        if LADDR in config_watcher.config and RADDR in config_watcher.config:
            # TODO: Write to prometheus
            pass

        if self.console_mode:
            self.request_df = self.request_df.append({
                "PID": event.pid,
                "COMM": event.task.decode('utf-8', 'replace'),
                "LADDR": LADDR,
                "LPORT": event.ports >> 32,
                "RADDR": RADDR,
                "RPORT": event.ports & 0xffffffff,
                "TX_KB": event.tx_b,
                "RX_KB": event.rx_b,
                "MS": float(event.span_us) / 1000,
            }, ignore_index=True)
            self.request_df = self.request_df[-10:]

    def poll_requests(self):
        while True:
            self.b.perf_buffer_poll()

    def poll_kube_api(self):
        pass

    def poll_syn_backlog(self):
        while True:
            data = self.syn_backlog_buffer.items()
            self.syn_df["outdated"] = True
            for row in data:
                saddr = inet_ntop(AF_INET, pack("I", row[0].saddr))

                if saddr in config_watcher.config:
                    # TODO: Write to prometheus
                    pass

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

        if not self.console_mode:
            poll_syn_backlog.join()
            poll_requests.join()
