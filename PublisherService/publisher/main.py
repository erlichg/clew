import json
import asyncio
import json
import os
import site

from aio_pika import connect, ExchangeType, Message, DeliveryMode


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))


async def _main(loop):
    connection, exchange = await setup_rabbitmq(loop)
    await publish_events(exchange)
    await connection.close()


async def setup_rabbitmq(loop):
    connection = await connect(host=os.environ.get('RABBIT_HOST'),
                               login=os.environ.get('RABBIT_USER'),
                               password=os.environ.get('RABBIT_PASS'),
                               loop=loop
                               )
    # Creating a channel
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        "meds", ExchangeType.FANOUT
    )
    queue = await channel.declare_queue(name='events')

    await queue.bind(exchange, "new.events")
    return connection, exchange


async def publish_events(exchange):
    dir = site.getsitepackages()[0]
    file = os.path.join(dir, 'publisher', 'events.json')
    with open(file) as f:
        events = json.load(f)
        for event in events:
            message = Message(
                json.dumps(event).encode(),
                delivery_mode=DeliveryMode.PERSISTENT
            )
            await exchange.publish(message, routing_key="new.events")
        print("pushed all events to RabbitMQ")


if __name__ == '__main__':
    main()
