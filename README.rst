Chrome Edit Server
==================

.. image:: https://travis-ci.org/coddingtonbear/chrome-edit-server.svg?branch=master
    :target: https://travis-ci.org/coddingtonbear/chrome-edit-server

.. image:: https://badge.fury.io/py/chrome-edit-server.png
    :target: http://badge.fury.io/py/chrome-edit-server

.. image:: https://pypip.in/d/chrome-edit-server/badge.png
    :target: https://pypi.python.org/pypi/chrome-edit-server

This application is an "edit server" supporting one of the many Chrome plugins
(including `TextAid <https://chrome.google.com/webstore/detail/textaid/ppoadiihggafnhokfkpphojggcdigllp>`_
and `Edit with Emacs <https://chrome.google.com/webstore/detail/edit-with-emacs/ljobjlafonikaiipfkggjbhkghgicgoh>`_)
allowing you to edit text area fields displayed in your browser using your editor-of-choice.

Getting Started
---------------

First, install this package from PyPI::

    pip install chrome-edit-server

Second, run the server by running::

    chrome-edit-server

Then, install either the `TextAid <https://chrome.google.com/webstore/detail/textaid/ppoadiihggafnhokfkpphojggcdigllp>`_
or `Edit with Emacs <https://chrome.google.com/webstore/detail/edit-with-emacs/ljobjlafonikaiipfkggjbhkghgicgoh>`_ 
Chrome extensions.  Follow the extension's instructions regarding how to open up an editor window.

Configuration
-------------

By default, the edit server will run on port 9292, and will use GVim (`gvim -f`)
as your editor, but you can configure each of those parameters by either setting
environment variables or providing arguments from the command line.

To see what options are available and how to set them, run::

  chrome-edit-server --help

Contributors
------------

This is an unofficial (but `endorsed <https://github.com/gfxmonk/edit-server/pull/5#issuecomment-53051767>`_) fork of
`@gfxmonk <https://github.com/gfxmonk>`_'s `edit-server <https://github.com/gfxmonk/edit-server>`_ repository that follows
common Python style conventions, and is packaged for distribution on PyPI.

If you have any thanks to give for this application's existence -- you owe them
to that gentleman.
