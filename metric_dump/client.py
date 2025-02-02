import requests
import datetime
import click
import time
import os
import random
import logging
import asyncio
from collections import defaultdict

logger = logging.getLogger()

metric_server_url = "http://localhost:22222"
auth_tuple = ("metric_user", "metric_password")


def net_post(client_id: str, kv_pairs: dict):
    response = requests.post(metric_server_url, json=kv_pairs, auth=auth_tuple)
    logger.debug(response)

def timestamp():
    """Return the time in microseconds."""
    return int(round(time.time()*1000000))

class Zone():
    current_stack = defaultdict(list)
    zone_names = set()

    def __init__(self, client_id, name, *, async_id=None):
        Zone.zone_names.add(name)
        self.client_id = client_id
        self.pid = os.getpid()
        self.name = name
        self.is_async = async_id is not None
        self.start = timestamp()
        self.fields = {
                "name": self.name,
                "pid": self.pid,
                "cat": "PERF",
                }
        if async_id is not None:
            self.fields["id"] = int(hash(async_id))
            self.fields["cat"] = async_id
        sendable = {
                "ph": "b" if self.is_async else "B",
                "ts": timestamp(),
                }
        sendable.update(self.fields)
        net_post(self.client_id, sendable)

    def __del__(self):
        sendable = {
                "ph": "e" if self.is_async else "E",
                "ts": timestamp()
                }
        sendable.update(self.fields)
        net_post(self.client_id, sendable)
        # can use "ph": "D" in future.

async def run_random(client_id, name, event_count, pause_length):
    local_use = random.randrange(max(1,(event_count // 3)))+1  # rand from 1 to 1/3 event_count
    event_count -= local_use

    zone = Zone(client_id, f"{name}_{local_use}/{event_count}", async_id=f"{name}")


    tasks = []

    if event_count > 0:
        # spawn of n tasks to handle the event_coutn
        spawns = random.randrange(event_count)+1  # random number of spawns
        spawns = random.randrange(spawns)+1  # but prefer fewer

        events_per_spawn = event_count // spawns
        for spawn in range(spawns):
            events = events_per_spawn if event_count > events_per_spawn else event_count
            event_count -= events
            tasks.append(asyncio.create_task(run_random(client_id, f"{name}.s{spawn}({events})", events, pause_length)))

    while local_use:
        pause_seconds = random.randrange(pause_length * 0.1, pause_length) / 1000
        work = Zone(client_id, f"{name}:work({local_use}:{int(1000*pause_seconds)})", async_id=f"{name}")
        await asyncio.sleep(pause_seconds)
        del work
        local_use -= 1

    # wait for subtasks
    for task in tasks:
        await task

    del zone


@click.command()
@click.argument("client_id", default=1234)
@click.option("-c", "--event-count", default=20, help="total number of events the random process will try to run")
@click.option("-p", "--pause-length", default=100, help="pause length in ms, but randomised between 10% to 100%")
@click.option("-n", "--processes", default=1, help="total number of sub-proceses to run")
def run_process(client_id, event_count, pause_length, processes):
    for process in range(processes):
        if os.fork() == 0:
            zone = Zone(client_id, f"run_process_ID_{process}")
            asyncio.run(run_random(client_id, "base", event_count, pause_length))
            del zone
            return
        time.sleep(random.randrange(pause_length * 0.1, pause_length) / 1000)
