from flask import Blueprint


class CustomBlueprint(Blueprint):
    gv = dict()
    def __init__(self, name, import_name, **kwargs):
        Blueprint.__init__(self, name, import_name, **kwargs)


###############################################################################
class ExceptionResponse(Exception):
    pass


###############################################################################
class NotFound(Exception):
    pass


###############################################################################
class ExceptionScheduleReduplicated(Exception):
    pass


