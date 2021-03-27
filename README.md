# Clew Medical Task by Avi Menashe

## Technology and overview
I have used the following main technologies:
* MySQL - database of the consumer service which saves the events, and from it builds the medication periods
* SQlite - for unit testing database (in memory)
* Flask - web server to provide REST API for the consumer service (list of periods for a specific patient)
* AsyncIO - to connect to rabbitMQ server using aio-pika (asyncio version of pika for connecting to RabbitMQ)
* RabbitMQ - for sending medical events using a common queue (accessed through AMQP protocol)
* Docker - to containerize the app and its envrionment (rabbitmq, mysql, consumer service, publisher service)
* Pytest - for running the unit test for each service
## Installation & Running
To install using docker, simply build the docker images and run in your favorite container (eg. kubernetes)
using docker-compose:
```
docker compose build
docker compose up -d
```
When running the services, they will run a python script called `wait-for-it` which will wait until Mysql / rabbitMQ TCP sockets are open, and after that, will connect to the servers and run the services

### Publisher service
the publisher service reads a JSON file which contains all of the medical events, and will send to the message broker (RabbitMQ) one by one to simulate a real medicine administration device.

### Unit tests
In your docker container, run `pytest` of each service

### Sample query for the consumer service
#### in PowerShell (Windows):
```
Invoke-RestMethod 'http://localhost:4567/api/v1/medication_periods/avi123' -Method 'GET' -Headers $headers | ConvertTo-Json
```
#### in Bash/cURL:
```
curl --location --request GET 'http://localhost:4567/api/v1/medication_periods/avi123'
```

### Expected input (Json file)
```
[
  {
    "up_id": "avi123",
    "medication_name": "Propecia",
    "action": "stop",
    "event_time": "2021-03-24T19:23:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Propecia",
    "action": "start",
    "event_time": "2021-03-24T18:23:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Propecia",
    "action": "start",
    "event_time": "2021-03-24T19:40:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Propecia",
    "action": "stop",
    "event_time": "2021-03-24T21:00:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Propecia",
    "action": "start",
    "event_time": "2021-03-25T09:00:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Acamol",
    "action": "start",
    "event_time": "2021-03-24T18:50:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Acamol",
    "action": "stop",
    "event_time": "2021-03-24T19:43:56+0000"
  },
  {
    "up_id": "moshe123",
    "medication_name": "Dexamol",
    "action": "start",
    "event_time": "2021-03-24T19:00:56+0000"
  },
  {
    "up_id": "moshe123",
    "medication_name": "Dexamol",
    "action": "stop",
    "event_time": "2021-03-24T19:00:56+0000"
  },
  {
    "up_id": "dina123",
    "medication_name": "Iron",
    "action": "start",
    "event_time": "2021-03-24T19:10:56+0000"
  },
  {
    "up_id": "dina123",
    "medication_name": "Iron",
    "action": "cancel_start",
    "event_time": "2021-03-24T19:12:56+0000"
  },
  {
    "up_id": "haim123",
    "medication_name": "Zinc",
    "action": "start",
    "event_time": "2021-03-24T20:15:56+0000"
  },
  {
    "up_id": "haim123",
    "medication_name": "Zinc",
    "action": "stop",
    "event_time": "2021-03-24T21:15:56+0000"
  },
  {
    "up_id": "haim123",
    "medication_name": "Zinc",
    "action": "cancel_stop",
    "event_time": "2021-03-24T22:15:56+0000"
  },
  {
    "up_id": "haim123",
    "medication_name": "Zinc",
    "action": "stop",
    "event_time": "2021-03-24T23:15:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Zinc",
    "action": "stop",
    "event_time": "2021-03-24T23:15:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Multivitamin",
    "action": "start",
    "event_time": "2021-03-24T23:15:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Multivitamin",
    "action": "ppp",
    "event_time": "2021-03-24T23:15:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Multivitamin",
    "action": "start",
    "event_time": "2021-18-24T23:15:56+0000"
  },
  {
    "up_id": "",
    "medication_name": "Multivitamin",
    "action": "start",
    "event_time": "2021-18-24T23:15:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "",
    "action": "start",
    "event_time": "2021-18-24T23:15:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Multivitamin",
    "action": "",
    "event_time": "2021-18-24T23:15:56+0000"
  },
  {
    "up_id": "avi123",
    "medication_name": "Multivitamin",
    "action": "start",
    "event_time": ""
  },
  {
  }
]
```