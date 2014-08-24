import logging
import pkg_resources

from .util import try_call


logger = logging.getLogger(__name__)


class Filters(object):
    def __init__(self):
        self.filters = []

    def load(self):
        loaded_filters = []
        for entry_point in (
            pkg_resources.iter_entry_points(group='chrome_edit_server.plugins')
        ):
            try:
                loaded_filters.append(
                    entry_point.load()
                )
                logger.debug(
                    "Loaded filter '%s'", entry_point.name
                )
            except ImportError:
                continue

        self.filters = loaded_filters
        logger.debug("Loaded %s filters.", len(self.filters))

    def get_first(self, headers, contents):
        for filter_ in self.filters:
            match_result = try_call(
                filter_.match,
                'check filter match',
                args=(headers, contents)
            )
            if match_result:
                # return True to use `self`, otherwise uses the match_result
                return filter_ if match_result is True else match_result
        return None
