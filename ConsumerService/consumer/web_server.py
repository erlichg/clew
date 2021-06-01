from ConsumerService.consumer.utils import calculate_periods
from sanic import Sanic
from sanic.response import json as json_response
import os
import json
from ConsumerService.consumer.db import DB

class WebServer:
    app = Sanic('clew_medical')

    @app.route("/records/<id>")
    async def medical_periods(request, id):
        db = DB()  # Should already be set-up
        records = db.fetchall(f'select * from {os.environ.get("POSTGRES_TABLE")} where p_id=%s', (id))  # fetch all records
        try:
            ans = calculate_periods(records)  # calculate periods in try catch as I want to return proper answer even in error
        except Exception as e:
            return json_response({'error': str(e), 'data': []})
        return json_response(json.dumps({'error': None, 'data': ans}, default=str))

    

        
        
        
    