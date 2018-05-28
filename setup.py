#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.1dev'

print '''------------------------------
Installing fastqcReport version {}
------------------------------
'''.format(version)


setup(
    name='fastqcReport',
    version=version,
    author='lx Gui',
    author_email='guilixuan@gmail.com',
    keywords=['bioinformatics', 'NGS', 'QC'],
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    scripts=['scripts/qc_report'],
    install_requires=[
        'Jinja2',
        'configparser',
    ]

)


print '''------------------------------
fastqcReport installation complete!
------------------------------
'''
