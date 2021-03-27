import pytest
from peewee import SqliteDatabase

from db_settings import MedicalAdministration
from main import process_event, calculate_medication_periods


class Test:
    mock_db = SqliteDatabase(":memory:")
    models = (MedicalAdministration,)

    def setup_method(self, test_method):
        self.up_id = "test_user"
        self.up_id_2 = "test_user_2"
        self.medication_name = "lithium"
        self.medication_name_2 = "Paracetamol"
        self.mock_db.bind(self.models)
        self.mock_db.create_tables(self.models)

    def teardown_method(self, test_method):
        self.mock_db.drop_tables(self.models)

    @pytest.mark.asyncio
    async def test_basic_period(self):
        start_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "start",
            "event_time": "2021-03-27T08:33:34+0000"}
        await process_event(start_event)

        stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "stop",
            "event_time": "2021-03-27T10:33:34+0000"}
        await process_event(stop_event)

        periods = calculate_medication_periods(self.up_id)
        assert len(periods) == 1

    @pytest.mark.asyncio
    async def test_cancel_stop(self):
        start_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "start",
            "event_time": "2021-03-27T08:35:34+0000"}
        await process_event(start_event)

        stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "stop",
            "event_time": "2021-03-27T10:35:34+0000"}
        await process_event(stop_event)

        cancel_stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "cancel_stop",
            "event_time": "2021-03-27T11:33:34+0000"}
        await process_event(cancel_stop_event)

        periods = calculate_medication_periods(self.up_id)
        assert len(periods) == 0

    @pytest.mark.asyncio
    async def test_cancel_start(self):
        start_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "start",
            "event_time": "2021-04-27T08:35:34+0000"}
        await process_event(start_event)

        stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "stop",
            "event_time": "2021-04-27T10:35:34+0000"}
        await process_event(stop_event)

        cancel_stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "cancel_start",
            "event_time": "2021-04-27T12:33:34+0000"}
        await process_event(cancel_stop_event)

        periods = calculate_medication_periods(self.up_id)
        assert len(periods) == 0

    @pytest.mark.asyncio
    async def test_cancel_multiple_medications_for_same_user(self):
        start_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "start",
            "event_time": "2021-01-27T01:35:34+0000"}
        await process_event(start_event)

        stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "stop",
            "event_time": "2021-01-27T02:35:34+0000"}
        await process_event(stop_event)

        start_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name_2,
            "action": "start",
            "event_time": "2021-01-27T01:45:34+0000"}
        await process_event(start_event)

        stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "cancel_stop",
            "event_time": "2021-01-27T02:45:34+0000"}
        await process_event(stop_event)

        cancel_stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name_2,
            "action": "cancel_start",
            "event_time": "2021-01-27T01:55:34+0000"}
        await process_event(cancel_stop_event)

        periods = calculate_medication_periods(self.up_id)
        assert len(periods) == 0

    @pytest.mark.asyncio
    async def test_multiple_medications_for_same_user(self):
        start_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "start",
            "event_time": "2021-01-27T01:45:34+0000"}
        await process_event(start_event)

        stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "stop",
            "event_time": "2021-01-27T02:45:34+0000"}
        await process_event(stop_event)

        start_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name_2,
            "action": "start",
            "event_time": "2021-01-27T01:55:34+0000"}
        await process_event(start_event)

        stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name_2,
            "action": "stop",
            "event_time": "2021-01-27T02:55:34+0000"}
        await process_event(stop_event)

        periods = calculate_medication_periods(self.up_id)
        assert len(periods) == 2

    @pytest.mark.asyncio
    async def test_multiple_medications_different_users(self):
        stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "stop",
            "event_time": "2021-01-27T02:45:34+0000"}
        await process_event(stop_event)

        start_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "start",
            "event_time": "2021-01-27T01:45:34+0000"}
        await process_event(start_event)

        stop_event = {
            "up_id": self.up_id,
            "medication_name": self.medication_name,
            "action": "cancel_stop",
            "event_time": "2021-01-27T02:55:34+0000"}
        await process_event(stop_event)

        start_event = {
            "up_id": self.up_id_2,
            "medication_name": self.medication_name_2,
            "action": "stop",
            "event_time": "2021-01-27T03:55:34+0000"}
        await process_event(start_event)

        start_event = {
            "up_id": self.up_id_2,
            "medication_name": self.medication_name_2,
            "action": "start",
            "event_time": "2021-01-27T01:55:34+0000"}
        await process_event(start_event)

        periods = calculate_medication_periods(self.up_id)
        assert len(periods) == 0

        periods = calculate_medication_periods(self.up_id_2)
        assert len(periods) == 1