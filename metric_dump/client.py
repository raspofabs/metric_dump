import requests
import datetime
import click
import time
import os
import random
import logging
from collections import defaultdict

logger = logging.getLogger()

metric_server_url = "http://localhost:22222"
auth_tuple = ("metric_user", "metric_password")


def metric_small(client_id: str, key: str, value: str):
    response = requests.get(metric_server_url, params={str(key): str(value)}, auth=auth_tuple)
    logger.debug(response)


def metric_large(client_id: str, kv_pairs: dict):
    response = requests.post(metric_server_url, json=kv_pairs, auth=auth_tuple)
    logger.debug(response)

def timestamp():
    return round(time.time()*1000000)

class Zone():
    current_stack = defaultdict(list)
    zone_names = set()
    global_start = timestamp()

    def __init__(self, client_id, name):
        Zone.zone_names.add(name)
        self.client_id = client_id
        self.pid = os.getpid()
        self.name = name
        self.start = timestamp()
        metric_large(self.client_id, {"name": self.name, "pid": self.pid, "ph": "B", "cat": "PERF", "ts": self.start - Zone.global_start})

    def __del__(self):
        end = timestamp()
        metric_large(self.client_id, {"name": self.name, "pid": self.pid, "ph": "E", "cat": "PERF", "ts": end - Zone.global_start})
        # can use "ph": "D" in future.

@click.command()
@click.argument("client_id")
def send_tick(client_id):
    metric_small(client_id, "tick", str(datetime.datetime.now(datetime.timezone.utc)))

@click.command()
@click.argument("client_id")
def send_larger(client_id):
    metric_large(client_id, {"not_a_tick": 1234, "season": "winter", "cookies_per_second": 4.7})

def run_random(client_id, depth, event_count, pause_length):
    events_used = 0
    zone = Zone(client_id, f"run_random_{event_count}")
    while event_count:
        work = Zone(client_id, f"run_random_work{event_count}")
        time.sleep(random.randrange(pause_length * 0.1, pause_length) / 1000)
        del work
        event_count -= 1
        events_used += 1
        if random.randrange(6) > depth and event_count > 0:
            sub_call = Zone(client_id, f"run_random_spawn_{event_count}")
            sub_events = run_random(client_id, depth + 1, event_count, pause_length)
            del sub_call
            events_used += sub_events
            event_count -= sub_events
        if random.randrange(3) < depth:
            return events_used
    del zone
    return events_used


@click.command()
@click.argument("client_id")
@click.option("-c", "--event-count", default=20, help="total number of events the random process will try to run")
@click.option("-p", "--pause-length", default=100, help="pause length in ms, but randomised between 10% to 100%")
@click.option("-n", "--processes", default=5, help="total number of sub-proceses to run")
def run_process(client_id, event_count, pause_length, processes):
    for process in range(processes):
        if os.fork() == 0:
            zone = Zone(client_id, f"run_process_ID_{process}")
            run_random(client_id, 0, event_count, pause_length)
            del zone
            return
        time.sleep(random.randrange(pause_length * 0.1, pause_length) / 1000)
