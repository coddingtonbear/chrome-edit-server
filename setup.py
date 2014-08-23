import os
from setuptools import setup, find_packages

# Get Requirements
requirements_path = os.path.join(
    os.path.dirname(__file__),
    'requirements.txt',
)
try:
    from pip.req import parse_requirements
    requirements = [
        str(req.req) for req in parse_requirements(requirements_path)
    ]
except ImportError:
    requirements = []
    with open(requirements_path, 'r') as in_:
        requirements = [
            req for req in in_.readlines()
            if not req.startswith('-')
            and not req.startswith('#')
        ]

# Get Version
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
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'chrome_edit_server = edit_server.cmdline:main'
        ],
    }
)
