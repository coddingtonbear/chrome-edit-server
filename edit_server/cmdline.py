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


logger = logging.getLogger(__name__)


SYSTEMD_FIRST_SOCKET_FD = 3


def main(args=None):
    if args is None:
        args = sys.argv

    logging.basicConfig(level=logging.INFO)

    try:
        parser = OptionParser("usage: %prog [OPTIONS] <edit-cmd>")
        parser.add_option("-p", "--port", default=9292, type="int")
        parser.add_option(
            "-d", "--delay",
            help="delay (in minutes) before deleting unused files",
            default=5)
        parser.add_option(
            "--tempdir",
            default=os.environ.get("EDIT_SERVER_TEMP", None),
            help="location of temporary files "
                 "(defaults to /tmp, or $EDIT_SERVER_TEMP if defined)")
        parser.add_option(
            "--no-incremental",
            help="disable incremental edits "
                 "(a request will block until editor is finished)",
            default=True,
            dest='incremental',
            action='store_false')
        parser.add_option(
            "--no-filters",
            help="disable context-specific filters (e.g gmail compose filter)",
            default=True,
            dest='use_filters',
            action='store_false')
        opts, args = parser.parse_args(args)
        port = opts.port
        Handler.DELAY_IN_MINUTES = opts.delay
        Editor.INCREMENTAL = opts.incremental
        Editor.TEMP_DIR = opts.tempdir
        Handler.FILTERS = Filters()
        if opts.use_filters:
            Handler.FILTERS.load()

        if args:
            Editor.OPEN_CMD = args

        logger.info('edit-server PID is %s', os.getpid())
        server_args = [('localhost', int(port)), Handler]
        if os.environ.get('LISTEN_PID', None) == str(os.getpid()):
            httpserv = SocketInheritingHTTPServer(
                *server_args,
                fd=SYSTEMD_FIRST_SOCKET_FD
            )
            logger.info(
                'edit-server started on socket fd %s',
                SYSTEMD_FIRST_SOCKET_FD
            )
        else:
            httpserv = ThreadedHTTPServer(*server_args)
            logger.info('edit-server started on port %s', port)
        httpserv.table = {}
        httpserv.serve_forever()
    except KeyboardInterrupt:
        httpserv.socket.close()
