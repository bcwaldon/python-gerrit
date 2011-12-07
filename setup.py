
from setuptools import setup

setup(
    name="gerrit",
    version="0.0.1",
    author="Brian Waldon",
    author_email="bcwaldon@gmail.com",
    url="https://github.com/bcwaldon/python-gerrit",
    description="Client library for interacting with the Gerrit JSONRPC API",
    install_requires=['httplib2', 'SQLAlchemy'],
    packages=['gerrit'],
)
