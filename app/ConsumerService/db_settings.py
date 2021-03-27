import os

import peewee
from peewee import *

db = MySQLDatabase(os.environ.get('DB_NAME'),
                   user=os.environ.get('DB_USER'),
                   passwd=os.environ.get('DB_PASSWORD'),
                   host=os.environ.get('DB_HOST'))


class MedicalAdministration(peewee.Model):
    # when filtering by patient id, add index for speed
    up_id = peewee.CharField(index=True)
    # when filtering by medication name, add index for speed
    medication_name = peewee.CharField(index=True)
    # when filtering by action, add index for speed
    action = peewee.CharField(index=True)
    # when ordering by event time, add index for speed
    event_time = peewee.DateTimeField(index=True)

    class Meta:
        database = db
