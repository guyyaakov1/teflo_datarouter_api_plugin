import os
import re
from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([a-zA-Z0-9.]+)['"]''')


def get_version():
    init = open(os.path.join(ROOT, 'teflo_datarouter_plugin', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setup(
    name='teflo_datarouter_plugin',
    version=get_version(),
    description="Teflo report plugin for DataRouter API.",
    author="Red Hat Inc",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3",
    entry_points={
            'importer_plugins': 'datarouter_plugin = teflo_datarouter_plugin:DataRouterPlugin',
    }
)
