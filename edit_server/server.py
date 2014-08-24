# Copyright (C) 2009  David Hilley <davidhi@cc.gatech.edu>,
# Tim Cuthbertson <gfxmonk.net>, Adam Coddington <me@adamcoddington.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
import time
import os
import socket
import threading
import logging

from six.moves.BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from six.moves.socketserver import ThreadingMixIn

from .editor import Editor, EDITORS

os.environ['FROM_EDIT_SERVER'] = 'true'


logger = logging.getLogger(__name__)


class HttpError(RuntimeError):
    pass


class Handler(BaseHTTPRequestHandler):
    DELAY_IN_MINUTES = 5
    FILTERS = None

    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('edit-server is running.\n')
            return
        self.send_error(404, "GET Not Found: %s" % self.path)

    def _get_editor(self, contents, headers):
        logger.debug("EDITORS: %r", EDITORS)
        filename = self.headers.get("x-file")
        if filename in ('undefined', 'null'):
            filename = None  # that's not very pythonic, is it chaps?
        editor = None

        if filename is not None:
            logger.debug("Reusing editor for file: %s", filename)
            editor = EDITORS.get(filename, None)
            if editor is None:
                logger.warning(
                    "Could not find existing editor - "
                    "creating new one for filename: %s",
                    filename
                )

        if editor is None:
            filter_ = self.FILTERS.get_first(headers, contents)
            editor = Editor(contents, filter_)
            EDITORS[editor.filename] = editor
        return editor

    def _wait_for_edited_contents(self, editor):
        editor.wait_for_edit()

        if editor.success:
            return editor.contents
        else:
            raise HttpError(404, editor.error)

    def _respond(self, contents, editor):
        self.send_response(200)
        self.send_header('x-open', str(editor.still_open).lower())
        if editor.still_open:
            self.send_header('x-file', editor.filename)
        self.end_headers()
        self.wfile.write(contents.encode('utf-8'))

    def _delayed_remove(self, filename):
        def delayed_remove():
            logger.debug("Sleeping %s mins", self.DELAY_IN_MINUTES)
            time.sleep(self.DELAY_IN_MINUTES * 60)
            logger.debug("Removing file: %s", filename,)
            try:
                os.unlink(filename)
            except Exception:
                logger.error("Unable to unlink: %s", filename)
        thread = threading.Thread(target=delayed_remove)
        thread.daemon = True
        thread.start()

    def do_POST(self):
        try:
            logger.info("Incoming request: Headers:\n%s", self.headers)
            logger.debug("There are %s active editors", len(EDITORS))
            content_length = self.headers.get('content-length')
            if content_length is None:
                self.send_response(411)
                self.end_headers()
                return
            content_length = int(content_length)
            body = self.rfile.read(content_length)
            editor = self._get_editor(contents=body, headers=self.headers)
            contents = self._wait_for_edited_contents(editor)
            self._respond(contents=contents, editor=editor)
            if editor.finished:
                self._delayed_remove(editor.filename)
        except HttpError as ex:
            self.send_error(*ex.args)
        except Exception:
            logger.exception("Unhandled exception")
            self.send_error(404, "Not Found: %s" % self.path)
        logger.debug("POST complete")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class SocketInheritingHTTPServer(ThreadedHTTPServer):
    """
    A HttpServer subclass that takes over an inherited socket from systemd
    """
    def __init__(self, address_info, handler, fd, bind_and_activate=True):
        super(SocketInheritingHTTPServer, self).__init__(
            address_info,
            handler,
            bind_and_activate=False
        )
        self.socket = socket.fromfd(fd, self.address_family, self.socket_type)
        if bind_and_activate:
            # NOTE: systemd provides ready-bound sockets,
            # so we only need to activate:
            self.server_activate()
