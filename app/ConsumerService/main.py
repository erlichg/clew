import asyncio
import json
import os
from datetime import datetime
from threading import Thread

import aio_pika
from flask import Flask, jsonify

from db_settings import (MedicalAdministration as MedicalA,
                         MedicalAdministration)

app = Flask(__name__)
ISO8601_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def init_db():
    MedicalAdministration.create_table()


async def process_event(event):
    event_time = datetime.strptime(event.get("event_time"),
                                   ISO8601_FORMAT)

    MedicalA.create(
        up_id=event.get("up_id"),
        medication_name=event.get("medication_name"),
        action=event.get("action"),
        event_time=event_time
    ).save()


async def rabbitmq_consume(loop):
    connection = await aio_pika.connect_robust(
        loop=loop,
        host=os.environ.get('RABBIT_HOST'),
        login=os.environ.get('RABBIT_USER'),
        password=os.environ.get('RABBIT_PASS')
    )

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("medication_administration_events")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    event = json.loads(message.body)
                    await process_event(event)


def start_background_loop():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(rabbitmq_consume(loop))
    loop.close()


def get_period_from_starts(up_id, medication_name, first_start, second_start):
    period = {'start_time': first_start, 'end_time': None}
    events = MedicalA.select().where(
        (MedicalA.up_id == up_id) &
        (MedicalA.medication_name == medication_name) &
        (MedicalA.event_time >= first_start) &
        (MedicalA.event_time < second_start)
    ).order_by(MedicalA.event_time)

    for event in events:
        if event.action == 'cancel_start':
            return None
        if event.action == 'stop':
            period['end_time'] = event.event_time
        if event.action == 'cancel_stop':
            period['end_time'] = None

    if period['end_time'] is None:
        return None

    return period


@app.route('/api/v1/medication_periods/<up_id>')
def medication_periods(up_id):
    periods = calculate_medication_periods(up_id)
    return jsonify(periods)


def calculate_medication_periods(up_id):
    periods = []
    medical_administration_names = MedicalA.select(
        MedicalA.medication_name).where(MedicalA.up_id == up_id).distinct()

    for ma in medical_administration_names:
        medication_name = ma.medication_name
        medical_administration_start_times = MedicalA.select(
            MedicalA.event_time).where(
            (MedicalA.up_id == up_id) &
            (MedicalA.medication_name == medication_name) &
            (MedicalA.action == 'start')
        ).order_by(MedicalA.event_time)

        start_times = list(
            map(lambda e: e.event_time, medical_administration_start_times)
        )

        start_times.append(datetime.max)
        start_tuples = zip(start_times, start_times[1:])

        for start_tuple in start_tuples:
            period = get_period_from_starts(up_id, medication_name,
                                            start_tuple[0], start_tuple[1])
            if period is None:
                continue

            periods.append({'medication_name': medication_name,
                            'start_time': period['start_time'],
                            'end_time': period['end_time']})
    return periods


if __name__ == "__main__":
    init_db()

    t = Thread(target=start_background_loop, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=4567, debug=True)
