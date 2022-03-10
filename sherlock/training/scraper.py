from prometheus_api_client import PrometheusConnect, MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
from tqdm import tqdm

prom = PrometheusConnect(url="http://127.0.0.1:9090", disable_ssl=True)

queries = [
    {'name': 'requests_sent_per_minute', "query": 'rate(requests_sent_total[1m])'},
    {'name': 'requests_received_per_minute', "query": 'sum by (serviceName) (rate(requests_received_total[1m]))'},
    {'name': 'requests_duration_per_minute', "query": 'rate(request_duration_seconds_sum[1m])'},
    {'name': 'cpu_usage', "query": 'avg_over_time(cpu_seconds[1m])'},
    {'name': 'memory_usage', "query": 'avg_over_time(memory_usage_bytes[1m])'},
    {'name': 'acknowledged_bytes_per_minute', "query": 'rate(acknowledged_bytes_sum[1m])'},
    {'name': 'transmitted_bytes_per_minute', "query": 'rate(transmitted_bytes_sum[1m])'},
    {'name': 'syn_backlog_per_minute', "query": 'avg_over_time(backlog{level="1"}[1m])'},
    {'name': 'high_syn_backlog_per_minute', "query": 'sum by (serviceName) (avg_over_time(backlog{level!="1"}[1m]))'},
]


for query in tqdm(queries):

    start_time = parse_datetime("41h")
    end_time = parse_datetime("20h")

    metric_data = prom.custom_query_range(
        query['query'],  # this is the metric name and label config
        start_time=start_time,
        end_time=end_time,
        step="15",
    )

    metric_df = MetricRangeDataFrame(metric_data, columns=['timestamp', 'serviceName', 'value'])

    metric_df['value'] = metric_df['value'].apply(float)
    metric_df.reset_index(inplace=True)

    metric_df.to_json(f"data/{query['name']}.json", orient="records", indent=4)
