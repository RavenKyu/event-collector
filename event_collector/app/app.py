import os
import yaml
import logging.config
import logging.handlers

from flask import Flask

from event_collector.collector import EventCollector
from event_collector.app.api.v1.events import bp as api_v1

_ROOT = os.path.abspath(os.path.dirname(__file__))
file = os.path.join(_ROOT + '/../', 'utils', 'logger.cfg')

with open(file) as f:
    logging_handler = yaml.safe_load(f)
logging.config.dictConfig(logging_handler)

collector = EventCollector()

app = Flask(__name__)
app.register_blueprint(api_v1, url_prefix='/api/v1/events')
api_v1.gv['collector'] = collector



