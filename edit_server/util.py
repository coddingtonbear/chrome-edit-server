import logging
import os
import shlex


logger = logging.getLogger(__name__)


def try_call(callable_, desc, default=None, args=None, kwargs=None):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    try:
        return callable_(*args, **kwargs)
    except Exception:
        logger.error("Failed to %s:", desc, exc_info=True)
        return default


def as_bool(value):
    if value.strip().lower() in ('y', 'yes', 'true', 'on'):
        return True
    return False


def as_command_args(value):
    return shlex.split(value, comments=False)


def get_environ(variable_name, default=None, type_=None):
    value = os.environ.get(variable_name, None)
    if value is None:
        return default
    if not type_:
        return value
    return type_(value)
