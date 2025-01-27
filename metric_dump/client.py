import requests
import datetime
import click

metric_server_url = "http://localhost:22222"
auth_tuple = ("metric_user", "metric_password")

def metric_small(client_id: str, key: str, value: str):
    response = requests.get(metric_server_url, params={str(key): str(value)}, auth=auth_tuple)
    print(response)
    pass


def metric_large(client_id: str, kv_pairs: dict):
    response = requests.post(metric_server_url, json=kv_pairs, auth=auth_tuple)
    print(response)
    pass


@click.command()
@click.argument("client_id")
def send_tick(client_id):
    metric_small(client_id, "tick", str(datetime.datetime.now(datetime.timezone.utc)))

@click.command()
@click.argument("client_id")
def send_larger(client_id):
    metric_large(client_id, {"not_a_tick": 1234, "season": "winter", "cookies_per_second": 4.7})
