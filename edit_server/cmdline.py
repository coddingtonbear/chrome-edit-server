import logging
from optparse import OptionParser
import os
import sys

from .editor import Editor
from .filters import Filters
from .server import (
    Handler,
    SocketInheritingHTTPServer,
    ThreadedHTTPServer,
)
from . import settings


logger = logging.getLogger(__name__)


def main(args=None):
    if args is None:
        args = sys.argv

    parser = OptionParser("usage: %prog [OPTIONS] <edit-cmd>")
    parser.add_option(
        "-p",
        "--port",
        default=settings.PORT,
        help=(
            "port on which edit server will listen "
            "for incoming connections"
        ),
        type="int"
    )
    parser.add_option(
        "-d",
        "--delay",
        help="delay (in minutes) before deleting unused files",
        default=settings.DELETE_DELAY
    )
    parser.add_option(
        "--tempdir",
        help=(
            "location of temporary files "
            "(defaults to /tmp, or $EDIT_SERVER_TEMP if defined)"
        ),
        default=settings.TEMP_FOLDER,
    )
    parser.add_option(
        "--no-incremental",
        help=(
            "disable incremental edits "
            "(a request will block until editor is finished)"
        ),
        default=settings.INCREMENTAL_ENABLED,
        dest='incremental',
        action='store_false'
    )
    parser.add_option(
        "--no-filters",
        help=(
            "disable context-specific filters "
            "(e.g gmail compose filter)"
        ),
        default=settings.FILTERS_ENABLED,
        dest='use_filters',
        action='store_false'
    )
    parser.add_option(
        "--loglevel",
        help=(
            "Logging verbosity level; set to 'DEBUG' to see "
            "all logging messages"
        ),
        default='INFO',
    )
    opts, args = parser.parse_args(args)

    logging.basicConfig(
        level=logging.getLevelName(opts.loglevel)
    )

    logger.debug("Starting edit server with options:")
    for option_name, option_value in vars(opts).items():
        logger.debug(
            "    %s = %s",
            option_name,
            option_value,
        )

    port = opts.port
    Handler.DELAY_IN_MINUTES = opts.delay
    Editor.INCREMENTAL = opts.incremental
    Editor.TEMP_DIR = opts.tempdir
    Handler.FILTERS = Filters()
    if opts.use_filters:
        Handler.FILTERS.load()

    if args:
        Editor.OPEN_CMD = args

    try:
        logger.info('edit-server PID is %s', os.getpid())
        server_args = [('localhost', int(port)), Handler]
        if os.environ.get('LISTEN_PID', None) == str(os.getpid()):
            httpserv = SocketInheritingHTTPServer(
                *server_args,
                fd=settings.SYSTEMD_FIRST_SOCKET_FD
            )
            logger.info(
                'edit-server started on socket fd %s',
                settings.SYSTEMD_FIRST_SOCKET_FD
            )
        else:
            httpserv = ThreadedHTTPServer(*server_args)
            logger.info('edit-server started on port %s', port)
        httpserv.table = {}
        httpserv.serve_forever()
    except KeyboardInterrupt:
        httpserv.socket.close()
