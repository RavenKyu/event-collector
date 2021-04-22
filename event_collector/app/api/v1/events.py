import flask
import operator
from flask import request, abort, make_response
from flask import jsonify, redirect, url_for
from functools import wraps
from event_collector.app import CustomBlueprint
from event_collector.utils.logger import get_logger

from event_collector.app import (
    ExceptionResponse,
    ExceptionScheduleReduplicated,
    NotFound)

logger = get_logger('api-v1')
bp = CustomBlueprint('api', __name__)


###############################################################################
def custom_error(message, status_code):
    msg = dict(message=message)
    return make_response(jsonify(msg), status_code)


###############################################################################
def result(f):
    @wraps(f)
    def func(*args, **kwargs):
        try:
            r = f(*args, **kwargs)
            return jsonify(r)
        except ExceptionScheduleReduplicated as e:
            return custom_error(str(e), 400)
        except NotFound as e:
            return custom_error(str(e), 404)
        except Exception as e:
            logger.exception(msg=str(e), exc_info=e)
            raise
    return func


###############################################################################
@bp.route('/', methods=('GET', 'POST'))
@result
def event():
    # requesting all of the collecting schedule with json format
    collector = bp.gv['collector']
    if request.method == 'GET':
        return collector.events

    elif request.method == 'POST':
        collector.event()

###############################################################################
@bp.route('/emit', methods=('POST', ))
@result
def emit():
    # requesting all of the collecting schedule with json format
    collector = bp.gv['collector']
    if request.method == 'POST':
        d = request.get_json(force=True)
        collector.check_event(d)