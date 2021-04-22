from flask import Flask

from event_collector.collector import EventCollector
from event_collector.app.api.v1.events import bp as api_v1

collector = EventCollector()

app = Flask(__name__)
app.register_blueprint(api_v1, url_prefix='/api/v1/events')
api_v1.gv['collector'] = collector



