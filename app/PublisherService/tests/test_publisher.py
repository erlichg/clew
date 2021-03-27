from main import connect_to_queue, publish_events


def test_publish():
    q_name = 'TEST_medication_administration_events'
    channel, connection = connect_to_queue(q_name)
    with connection:
        print("purging queue")
        channel.queue_purge(q_name)

        publish_events(channel)

        # check existing messages
        message = channel.basic_get(q_name, auto_ack=True)
        assert message is not (None, None, None)
