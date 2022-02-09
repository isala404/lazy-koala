from gazer import Gazer
from prometheus_client import start_http_server

gazer = Gazer()
start_http_server(8000)
gazer.poll_data_in_bg()
