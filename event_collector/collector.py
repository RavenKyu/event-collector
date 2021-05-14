import os
import types
import operator
import logging
import json
import inspect
import traceback
from celery import Celery

from event_collector import (ExceptionResponse, ExceptionScheduleReduplicated)

BROKER_URL = os.environ.setdefault('BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.setdefault('CELERY_RESULT_BACKEND',
                                              'redis://redis:6379/0')

logger = logging.getLogger(__name__)


###############################################################################
class EventCollector:
    def __init__(self):
        self.events = dict()
        self.__global_store = dict()
        self.job_broker = Celery(
            'event-jobs', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND,)

    # =========================================================================
    def add_events(self, events):
        logger.debug('Adding events with template.')
        for event in events:
            event_name = operator.itemgetter('event_name')(event)
            event_names = [x for x in self.events.keys()]
            if event_name in event_names:
                msg = f'The event name \'{event_name}\' is already assigned.'
                logger.error(msg)
                raise ExceptionScheduleReduplicated(msg)

            self.events[event_name] = event
            self.__global_store[event_name] = {'_gv': dict()}

    # =========================================================================
    def remove_event(self, event_name: str):
        logger.debug(f'Removing a event: {event_name}')
        try:

            del self.events[event_name]
            del self.__global_store[event_name]
        except KeyError:
            logger.warning(
                f'Failed to find the event name "{event_name}". '
                f'in the event list')
        return

    # =========================================================================
    @staticmethod
    def get_python_module(code, name):
        module = types.ModuleType(name)
        exec(code, module.__dict__)
        return module

    # =========================================================================
    @staticmethod
    def insert_number_each_line(data: str):
        result = list()
        data = data.split('\n')
        for (number, line) in enumerate(data):
            result.append(f'{number + 1:04} {line}')
        return '\n'.join(result)

    # =========================================================================
    @staticmethod
    def filter_dict(dict_to_filter, thing_with_kwargs):
        sig = inspect.signature(thing_with_kwargs)
        filter_keys = [param.name for param in sig.parameters.values() if
                       param.kind == param.POSITIONAL_OR_KEYWORD]
        filtered_dict = {filter_key: dict_to_filter[filter_key] for filter_key
                         in filter_keys}
        return filtered_dict

    # =========================================================================
    def _source(self, name, setting):
        logger.debug(f'{name} - Preparing to execute the script.')
        source_type, code, arguments = operator.itemgetter(
            'type', 'code', 'arguments')(setting)
        module = EventCollector.get_python_module(code, name)
        try:
            _gv = self.__global_store[name]
            arguments = {**arguments, **_gv}
            filtered_arguments = EventCollector.filter_dict(
                arguments, module.main)
            logger.debug(f'{name} - Executing the script')
            data = module.main(**filtered_arguments)
        except Exception as e:
            code = EventCollector.insert_number_each_line(code)
            logger.error(f'{e}\ncode: \n{code}')
            raise
        return data

    # =========================================================================
    def get_matched_events(self, event):
        """
        returning matched events with event templates
        :param event:
            {'type': 'data-collector', 'schedule_name': schedule_name}
        :return:
        """
        events = list()

        for e in [e for e in self.events.values()]:
            if e['event'] == event['event']:
                events.append(e)
        return events

    # =========================================================================
    def get_condition_codes(self, name, conditions):
        codes = list()
        for c in conditions:

            module = EventCollector.get_python_module(c['code'], 'condition')
            codes.append((module, c['code']))
        return codes

    # =========================================================================
    def check_event(self, event):
        # event = {
        #     'name': 'schedule_name'
        #     'event': {
        #         'type': 'data-collector',
        #         'schedule_name': schedule_name},
        #     'data': data
        # }
        # 등록된 이벤트 목록 안에서 요청받은 이벤트와 매치되는 이벤트 검색
        logger.debug('Checking event ...')
        events = self.get_matched_events(event)
        # 매치된 이벤트 목록에서 각각 컨디션 검사
        for e in events:
            codes = self.get_condition_codes(e['event_name'], e['conditions'])
            _gv = self.__global_store[e['event_name']]
            data = json.loads(event['data'])
            arguments = {**{'data': data}, **_gv}
            for module, code in codes:
                try:
                    if not bool(module.main(**arguments)):
                        logger.debug('the condition is not matched')
                        break
                except Exception as e:
                    code = EventCollector.insert_number_each_line(code)
                    logger.error(f'{e}\ncode: \n{code}')
                    traceback.print_exc()
                    break

                # 컨디션에 통과된 이벤트는 개별 실행을 위해 셀러리큐로 보내기전 전달할 값을 생성
                for action in e['actions']:
                    try:
                        logger.debug('Generating arguments of action')
                        code = action['arguments']
                        module = EventCollector.get_python_module(
                            code, 'condition-action')
                        arguments = module.main(**arguments)
                    except Exception as e:
                        code = EventCollector.insert_number_each_line(code)
                        logger.error(f'{e}\ncode: \n{code}')
                        traceback.print_exc()
                        break

                    # 셀러리큐 전달
                    logger.debug('Requesting to call the action '
                                 f'for the event - {events}')
                    self.job_broker.send_task(
                        action['function'], args=(arguments, ), kwargs={})


