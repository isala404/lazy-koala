#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports
#
# tcplife   Trace the lifespan of TCP sessions and summarize.
#           For Linux, uses BCC, BPF. Embedded C.
#
# USAGE: tcplife [-h] [-C] [-S] [-p PID] [-4 | -6] [interval [count]]
#
# This uses the sock:inet_sock_set_state tracepoint if it exists (added to
# Linux 4.16, and replacing the earlier tcp:tcp_set_state), else it uses
# kernel dynamic tracing of tcp_set_state().
#
# While throughput counters are emitted, they are fetched in a low-overhead
# manner: reading members of the tcp_info struct on TCP close. ie, we do not
# trace send/receive.
#
# Copyright 2016 Netflix, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# IDEA: Julia Evans
#
# 18-Oct-2016   Brendan Gregg   Created this.
# 29-Dec-2017      "      "     Added tracepoint support.

from __future__ import print_function

import time

from bcc import BPF
import argparse
from socket import inet_ntop, AF_INET, inet_aton
from struct import pack, unpack

# arguments
examples = """examples:
    ./tcplife           # trace all TCP connect()s
    ./tcplife -T        # include time column (HH:MM:SS)
    ./tcplife -w        # wider columns (fit IPv6)
    ./tcplife -stT      # csv output, with times & timestamps
    ./tcplife -p 181    # only trace PID 181
    ./tcplife -L 80     # only trace local port 80
    ./tcplife -L 80,81  # only trace local ports 80 and 81
    ./tcplife -D 80     # only trace remote port 80
    ./tcplife -4        # only trace IPv4 family
    ./tcplife -6        # only trace IPv6 family
"""
parser = argparse.ArgumentParser(
    description="Trace the lifespan of TCP sessions and summarize",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-w", "--wide", action="store_true",
                    help="wide column output (fits IPv6 addresses)")
parser.add_argument("-p", "--pid",
                    help="trace this PID only")
parser.add_argument("-a", "--addr",
                    help="filter for address")
parser.add_argument("--ebpf", action="store_true",
                    help=argparse.SUPPRESS)
args = parser.parse_args()
debug = 0

# define BPF program
with open('bpf.c', 'r') as f:
    bpf_text = f.read()

with open('sock_state.c', 'r') as f:
    bpf_text += f.read()

with open('syn_backlog.c', 'r') as f:
    bpf_text += f.read()

# code substitutions
if args.pid:
    bpf_text = bpf_text.replace('FILTER_PID',
                                'if (pid != %s) { return 0; }' % args.pid)

if args.addr:
    bpf_text = bpf_text.replace('ADDRFILTER',
                                """if (data4.saddr != {0} || data4.daddr != {0}) 
                                return 0;""".format(unpack("=I", inet_aton(args.addr))[0]))

bpf_text = bpf_text.replace('FILTER_PID', '')
bpf_text = bpf_text.replace('ADDRFILTER', '')

#
# Setup output formats
#
# Don't change the default output (next 2 lines): this fits in 80 chars. I
# know it doesn't have NS or UIDs etc. I know. If you really, really, really
# need to add columns, columns that solve real actual problems, I'd start by
# adding an extended mode (-x) to included those columns.
#
header_string = "%-5s %-10.10s %s%-15s %-5s %-15s %-5s %5s %5s %s"
format_string = "%-5d %-10.10s %s%-15s %-5d %-15s %-5d %5d %5d %.2f"


# process event
def print_ipv4_event(cpu, data, size):
    event = b["ipv4_events"].event(data)
    print(format_string % (event.pid, event.task.decode('utf-8', 'replace'),
                           "",
                           inet_ntop(AF_INET, pack("I", event.saddr)), event.ports >> 32,
                           inet_ntop(AF_INET, pack("I", event.daddr)), event.ports & 0xffffffff,
                           event.tx_b, event.rx_b, float(event.span_us) / 1000))


# initialize BPF
b = BPF(text=bpf_text)

# header
print(header_string % ("PID", "COMM", "", "LADDR",
                       "LPORT", "RADDR", "RPORT", "TX_KB", "RX_KB", "MS"))

start_ts = 0

# read events
b["ipv4_events"].open_perf_buffer(print_ipv4_event, page_cnt=64)
# b.attach_kprobe(event="tcp_v4_syn_recv_sock", fn_name="update_syn_backlog")
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        # exit()
        break

# while True:
#     try:
#         time.sleep(999999)
#     except KeyboardInterrupt:
#         break

dist = b['syn_backlog']
print()
for item in dist.items():
    print({"backlog": item[0].backlog,
           "slot": item[0].slot,
           "saddr": inet_ntop(AF_INET, pack("I", item[0].saddr)),
           "lport": item[0].lport,
           "value": item[1].value})


