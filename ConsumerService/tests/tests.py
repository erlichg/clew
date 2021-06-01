import unittest
from ConsumerService.consumer.utils import calculate_periods


class TestPeriodCalculationMethods(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(calculate_periods([]), {})

    def test_double_start(self):
        with self.assertRaises(Exception):
            calculate_periods([
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "start",
                    "event_time": "2021-01-01T00:00:00+0000"
                },
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "start",
                    "event_time": "2021-01-01T01:00:00+0000"
                }
            ])

    def test_stop_without_start(self):
        with self.assertRaises(Exception):
            calculate_periods([
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "stop",
                    "event_time": "2021-01-01T00:00:00+0000"
                }
            ])

    def test_cancel_start(self):
        with self.assertRaises(Exception):
            calculate_periods([
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "cancel_start",
                    "event_time": "2021-01-01T00:00:00+0000"
                }
            ])

    def test_cancel_stop_without_start(self):
        with self.assertRaises(Exception):
            calculate_periods([
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "start",
                    "event_time": "2021-01-01T00:00:00+0000"
                },
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "cancel_stop",
                    "event_time": "2021-01-01T01:00:00+0000"
                }
            ])

    def test_same_time(self):
        self.assertEqual(calculate_periods([
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
                    "event_time": "2021-01-01T00:00:00+0000"
                }
            ]), {'X': [("2021-01-01T00:00:00+0000", "2021-01-01T00:00:00+0000")]})

    def test_open_period(self):
        self.assertEqual(calculate_periods([
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "start",
                    "event_time": "2021-01-01T00:00:00+0000"
                }
            ]), {'X': [("2021-01-01T00:00:00+0000",)]})

    def test_cancel_start(self):
        self.assertEqual(calculate_periods([
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "start",
                    "event_time": "2021-01-01T00:00:00+0000"
                },
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "cancel_start",
                    "event_time": "2021-01-01T01:00:00+0000"
                },
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "start",
                    "event_time": "2021-01-01T02:00:00+0000"
                },
                {
                    "p_id": "1",
                    "medication_name": "X",
                    "action": "stop",
                    "event_time": "2021-01-01T03:00:00+0000"
                }
            ]), {'X': [("2021-01-01T02:00:00+0000", "2021-01-01T03:00:00+0000")]})

    def test_simple_period(self):
        self.assertEqual(calculate_periods([
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
            ]), {'X': [("2021-01-01T00:00:00+0000", "2021-01-01T01:00:00+0000")]})


if __name__ == '__main__':
    unittest.main()
