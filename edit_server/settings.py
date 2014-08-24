from .util import as_bool, as_command_args, get_environ


# Command to use for launching edit server
OPEN_CMD = get_environ('EDIT_SERVER_EDITOR', ['gvim', '-f'], as_command_args)

# Port on which chrome-edit-server will listen
PORT = get_environ('EDIT_SERVER_PORT', 9292, int)

# Time (in minutes) to wait after creating files to delete them
DELETE_DELAY = get_environ('EDIT_SERVER_DELETE_DELAY', 5, int)

# Place at which to store temporary files
TEMP_FOLDER = get_environ('EDIT_SERVER_TEMP')

# Enable incremental editing?
INCREMENTAL_ENABLED = get_environ('EDIT_SERVER_INCREMENTAL', True, as_bool)

# Enable filters?
FILTERS_ENABLED = get_environ('EDIT_SERVER_USE_FILTERS', True, as_bool)


SYSTEMD_FIRST_SOCKET_FD = 3
