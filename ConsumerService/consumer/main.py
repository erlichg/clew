try:
    from ConsumerService.consumer.utils import ACTIONS
    from ConsumerService.consumer.db import DB
    from ConsumerService.consumer.web_server import WebServer
except:
    from .utils import ACTIONS
    from .db import DB
    from .web_server import WebServer
import json
import asyncio
import json
import os
import sys

from aio_pika import connect, ExchangeType



DB_TABLE = os.environ.get('POSTGRES_TABLE')
db = DB()  # Global variable to DB
loop = asyncio.get_event_loop()


def setup_db():
    """
    This methods sets up the DB connection and first configuration.
    """
    # call db.setup to initiate the connection
    db.setup(host=os.environ.get('POSTGRES_HOST'),
            database=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD'))
    
    # create table if not already exists
    db.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_TABLE} (
            event_id SERIAL PRIMARY KEY,
            p_id VARCHAR(255) NOT NULL,
            medication_name VARCHAR(255) NOT NULL,
            action VARCHAR(255) NOT NULL,
            event_time TIMESTAMPTZ NOT NULL
        )
        """)


def main():
    try:
        db = setup_db()
    except:
        print('Error connecting to postgres DB')
        sys.exit(1)

    # Start web server for API calls
    print('Starting WebServer')
    web = WebServer()
    srv = loop.run_until_complete(web.app.create_server(host=os.environ.get('WEB_ADDR'), port=int(os.environ.get('WEB_PORT')), return_asyncio_server=True,
        asyncio_server_kwargs=dict(
            start_serving=True
        )))

    # Start async consumer
    print('Starting consumer')
    loop.create_task(setup_rabbitmq())

    # we enter a never-ending loop that waits for data
    # and runs callbacks whenever necessary.
    print(" [*] Waiting for logs. To exit press CTRL+C")
    loop.run_until_complete(srv.serve_forever())
    print('consumer exiting')
    db.close()
    web.app.stop()

async def on_message(message):
    """
    This method runs on every message received from queue. It just parses the json and adds to DB
    """
    async with message.process():
        try:
            msg = json.loads(message.body)
            if msg:
                if msg['action'] not in ACTIONS:
                    raise Exception('Invalid action')
                db.execute(f"""
                INSERT INTO {DB_TABLE}(p_id,medication_name,action,event_time) VALUES(%s,%s,%s,%s)
                """, (msg['p_id'], msg['medication_name'], msg['action'], msg['event_time']))
        except Exception as e:
            print('Error parsing message from queue: '+str(e))


async def setup_rabbitmq():
    """
    This method sets up the rabbitMQ connection
    """
    _try = 1
    while _try < 5:
        try:
            connection = await connect(host=os.environ.get('RABBIT_HOST'),
                                login=os.environ.get('RABBIT_USER'),
                                password=os.environ.get('RABBIT_PASS'),
                                loop=loop,
                                )
            break
        except:
            #try again
            _try = _try + 1
            await asyncio.sleep(5)
    if not connection:
        print('Error connecting to RabbitMQ')
        sys.exit(1)
    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    exchange = await channel.declare_exchange(
        "meds", ExchangeType.FANOUT
    )
    queue = await channel.declare_queue(name='events')

    await queue.bind(exchange, "new.events")
    await queue.consume(on_message)        

if __name__ == '__main__':
    main()
