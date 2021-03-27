import json
import os
from datetime import datetime

import pika

ACTIONS = ["start", "stop", "cancel_start", "cancel_stop"]


def validate_event(json_event):
    up_id = json_event.get("up_id", None)
    if up_id is None or up_id.strip() == "":
        return False

    medication_name = json_event.get("medication_name", None)
    if medication_name is None or medication_name.strip() == "":
        return False

    action = json_event.get("action", None)
    if action is None or action.strip() == "":
        return False
    if action not in ACTIONS:
        return False

    event_time = json_event.get("event_time", None)
    if event_time is None or event_time.strip() == "":
        return False
    try:
        datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        return False

    return True


def publish_events(channel):
    with open("medication_administration_events.json") as f:
        events = json.load(f)
        for event in events:
            if not validate_event(event):
                continue
            channel.basic_publish(exchange='',
                                  routing_key='medication_administration_events',
                                  body=str.encode(json.dumps(event)))

    print("pushed all events to RabbitMQ")


def connect_to_queue(queue_name):
    credentials = pika.PlainCredentials(os.environ.get('RABBIT_USER'),
                                        os.environ.get('RABBIT_PASS'))
    parameters = pika.ConnectionParameters(host=os.environ.get('RABBIT_HOST'),
                                           credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    return channel, connection


def connect_and_publish():
    channel, connection = connect_to_queue('medication_administration_events')
    with connection:
        publish_events(channel)


if __name__ == '__main__':
    connect_and_publish()
