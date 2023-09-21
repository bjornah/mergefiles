
from setuptools import setup, find_packages

setup(
    name='mergefiles',
    version='0.2',
    packages=find_packages(),
    install_requires=[],
    author='Björn Ahlgren',
    author_email='bjorn.victor.ahlgren@gmail.com',
    description='A utility to merge multiple directories into a single directory, with advanced options for merge conflicts',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
)
