# Lazy-Koala

Lazy Koala is a lightweight framework for root cause analysis in distributed systems. This provides all the tooling needed for RCA from instrumentation to storage and real-time processing of telemetry data using deep learning.

# Usage

```sh
git clone https://github.com/MrSupiri/lazy-koala
cd charts
helm install lazy-koala --generate-name -n lazy-koala --create-namespace
```

## Architecture

![High Level System Diagram](documentation/README/high-level-system-diagram.png)

## Repo Structure

```txt
./charts/lazy-koala - Helm Chart
./control-plane     - Kubernetes Operator which binds all the sub-components
./documentation     - Thesis written by the author about project
./gazer             - eBPF based telemetry extraction agent
./inspector         - Simple HTTP proxy to contact kubeAPI from the UI
./scripts           - Helper Scripts
./sherlock          - Inference agent to calculate anomaly scores
./ui                - User dashboard to visualize the system
```

# Demo

![DEMO](documentation/README/demo.gif)
