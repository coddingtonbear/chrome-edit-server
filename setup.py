import os
from setuptools import setup, find_packages

with open(
    os.path.join(
        os.path.dirname(__file__),
        'VERSION',
    ), 'r'
) as version_file:
    VERSION = version_file.read().strip()

setup(
    name='chrome-edit-server',
    version=VERSION,
    url='https://github.com/coddingtonbear/chrome-edit-server',
    description=(
        'An edit server compatible with TextAid and '
        '"Edit with Emacs" chrome extensions"'
    ),
    author='Tim Cuthbertson, Adam Coddington',
    author_email='me@adamcoddington.net',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'chrome_edit_server = edit_server.server:main'
        ],
    }
)
