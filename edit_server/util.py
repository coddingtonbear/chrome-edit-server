import logging


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
