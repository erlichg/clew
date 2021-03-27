import pytest
from peewee import SqliteDatabase

from db_settings import MedicalAdministration
from main import process_event, calculate_medication_periods


class Test:
    mock_db = SqliteDatabase(':memory:')
    models = (MedicalAdministration,)

    def setup_method(self, test_method):
        self.mock_db.bind(self.models)
        self.mock_db.create_tables(self.models)

    def teardown_method(self, test_method):
        self.mock_db.drop_tables(self.models)

    @pytest.mark.asyncio
    async def test_basic_period(self):
        start_event = {
            'up_id': 'test_111',
            'medication_name': 'lithium',
            'action': 'start',
            'event_time': '2021-03-27T08:33:34+0000'}
        await process_event(start_event)

        stop_event = {
            'up_id': 'test_111',
            'medication_name': 'lithium',
            'action': 'stop',
            'event_time': '2021-03-27T10:33:34+0000'}
        await process_event(stop_event)

        periods = calculate_medication_periods('test_111')
        assert len(periods) == 1

    @pytest.mark.asyncio
    async def test_cancel_stop(self):
        start_event = {
            'up_id': 'test_111',
            'medication_name': 'lithium',
            'action': 'start',
            'event_time': '2021-03-27T08:33:34+0000'}
        await process_event(start_event)

        stop_event = {
            'up_id': 'test_111',
            'medication_name': 'lithium',
            'action': 'stop',
            'event_time': '2021-03-27T10:33:34+0000'}
        await process_event(stop_event)

        cancel_stop_event = {
            'up_id': 'test_111',
            'medication_name': 'lithium',
            'action': 'cancel_stop',
            'event_time': '2021-03-27T11:33:34+0000'}
        await process_event(cancel_stop_event)

        periods = calculate_medication_periods('test_111')
        assert len(periods) == 0
