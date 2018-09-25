import os
from setuptools import setup
import git_auto_export

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='git-auto-export-sample',
    version=git_auto_export.__version__,
    packages=["git_auto_export"],
    include_package_data=True,
    license='GNU AFFERO GENERAL PUBLIC LICENSE',
    description='A task that auto save course OLX to git when author publish it',
    url='https://github.com/amir-qayyum-khan/git_auto_export_sample',
    install_requires=[
        'setuptools',
        'edx-opaque-keys',
        'celery',
    ],
)
