#!/usr/bin/env python

from distutils.core import setup

setup(
    name='16s_robot_perception',
    version='1.0',
    description='Solution library for 16SS Robot Perception class',
    author='Minh Nguyen',
    author_email='minh.nguyen@smail.inf.h-brs.de',
    packages=['normalized_dlt', 'ransac'],
    package_dir={'' : 'src'}
)
