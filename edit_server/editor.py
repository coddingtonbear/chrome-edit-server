import logging
import os
import stat
import subprocess
import tempfile
import time

from .util import try_call
from . import settings


logger = logging.getLogger(__name__)


EDITORS = {}


class Editor(object):
    INCREMENTAL = True
    OPEN_CMD = settings.OPEN_CMD
    TEMP_DIR = None

    def __init__(self, contents, filter_=None):
        logger.info("Editor using filter: %r", filter_)
        self.filter = filter_
        self.prefix = "chrome_"
        self._spawn(contents)

    def _spawn(self, contents):
        if self.filter is not None:
            try:
                contents = self.filter.decode(contents)
            except Exception:
                self.filter = None
                logger.error("Failed to decode contents:", exc_info=True)

        with tempfile.NamedTemporaryFile(
            delete=False,
            prefix=self.prefix,
            suffix='.txt',
            dir=self.TEMP_DIR
        ) as temp:
            temp.write(contents)
            self.filename = temp.name

        # spawn editor...
        cmd = self.OPEN_CMD + [temp.name]
        logger.info("Spawning editor: %r", cmd)
        self.process = subprocess.Popen(cmd, close_fds=True)
        self.returncode = None

    @property
    def still_open(self):
        return self.returncode is None

    @property
    def success(self):
        return self.still_open or self.returncode == 0

    @property
    def finished(self):
        return self.returncode is not None

    @property
    def error(self):
        if self.returncode > 0:
            return 'text editor returned %d' % self.returncode
        elif self.returncode < 0:
            return 'text editor died on signal %d' % -(self.returncode)

    @property
    def contents(self):
        with open(self.filename, 'r') as file_:
            contents = file_.read()
        if self.filter is not None:
            contents = try_call(
                self.filter.encode,
                'encode contents',
                args=(contents,),
                default=contents
            )
        return contents

    def wait_for_edit(self):
        def _finish():
            del EDITORS[self.filename]

        if not self.INCREMENTAL:
            self.returncode = self.process.wait()
            _finish()
            return
        last_mod_time = os.stat(self.filename)[stat.ST_MTIME]
        while True:
            time.sleep(1)
            self.returncode = self.process.poll()
            if self.finished:
                _finish()
                return
            mod_time = os.stat(self.filename)[stat.ST_MTIME]
            if mod_time != last_mod_time:
                logger.debug(
                    "New mod time: %s, last: %s",
                    mod_time,
                    last_mod_time
                )
                last_mod_time = mod_time
                return
