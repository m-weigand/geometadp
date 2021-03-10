#!/usr/bin/env python
# import os
# import glob

from setuptools import setup, find_packages

version_long = '0.1.0.dev0'

if __name__ == '__main__':
    setup(
        name='geometadp',
        version=version_long,
        description='Geophysical Metadata Picker',
        long_description=open('Readme.md', 'r').read(),
        long_description_content_type="text/markdown",
        author='Maximilian Weigand',
        author_email='mweigand@geo.uni-bonn.de',
        license='MIT',
        # url='https://github.com/geophysics-ubonn/reda',
        packages=find_packages("lib"),
        package_dir={'': 'lib'},
        install_requires=[
            'dicttoxml',
            'jupyter',
            'ipywidgets',
            'PyQT5',
        ],
        # classifiers=(
        #     "Programming Language :: Python :: 3",
        #     "License :: OSI Approved :: MIT License",
        #     "Operating System :: OS Independent",
        # ),
    )
