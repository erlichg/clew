# application-assignment

This project contains 4 dockers:
- Postgres DB
- RabbitMQ
- Publisher
- Consumer

## Publisher
The Publisher docker runs a python script that reads events from events.json file.
It then pushes these events to RabbitMQ and exits.
An event has the following fields: patient_id, medication_name, action and event_time.

## Consumer
The Consumer docker is an always on service. It listens to RabbitMQ and for each message received, it stores them in postgres DB.
It also raises a simple web server (port 8000) with one api: /records/<id> which returns a list of medication periods for patient with this id.
The api output is a dictionary with error and data keys.
The error is null if no error or a string of the error encountered in calculation.
The data is a dict with medication name as keys and values is a list of tuples that represent a period (start, end).
An open period (i.e. start without stop) is represented by (start, )

### How period calculation works
The raw events are first sorted by medication_name, event_time and action.
The order of actions is very important and is as follows: start, cancel_start, stop, cancel_stop.
After sorting, the code goes over the list and for every medication, calculates the periods.
Due to the sorting, it is guaranteed that the events will be one medication at a time so total period calculation for one medication is calculated before moving to the next.
It is also guaranteed that events are read by the actual event_time and not by the order they were received.
Finally, by sorting by the specific action order, I can detect invalid events as follows:
1. cancel_start without a previous start
2. cancel_stop without a previous stop
3. start not after stop
4. stop not after start

The code then runs one event at a time.
If encounter start, mark start of period and stop closes that period. 
cancel_start cancels the period and cancel_stop cancels the previous stopping period.


### Edge cases
1. If period starts but never finishes (no stop encountered), an open period is added (i.e. without an end time)
2. If several events are received at the same time, they are treated by the specific action order.
3. events with an invalid input are not stored in DB (action is checked and invalid date should throw error from DB when inserting)

## Tests
A unittest file is included in the Consumer package.
It tests all period calculation validations.
Further testing can be made on message receiving logic althout it is quite simple (just receiving the message and storing it).

## Optimizations
Currently all calculations are done when calling the API.
It is going sorting all events and going over them once so it is O(n log n) due to sorting.
It is also possible to move logic to message receiving logic. It depends on what is done more (i.e. if a lot of messages are received, it might be a lot to do calculations on every message received, however, if events are received at a more leisurely pace and api is called a lot, we can move the logic to there)

## Example
events.json
```
{
    "p_id": "1",
    "medication_name": "X",
    "action": "start",
    "event_time": "2021-01-01T00:00:00+0000"
},
{
    "p_id": "1",
    "medication_name": "X",
    "action": "stop",
    "event_time": "2021-01-01T01:00:00+0000"
}
```

calling consumer api
```
curl http://localhost:8000/records/1
{'error': null, 'data': {'X': [("2021-01-01T00:00:00+0000", "2021-01-01T01:00:00+0000")]}}
```