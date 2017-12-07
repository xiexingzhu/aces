# -*- coding: utf-8 -*-
# @Author: YangZhou
# @Date:   2017-06-19 13:38:47
# @Last Modified by:   YangZhou
# @Last Modified time: 2017-06-21 02:10:43
from setuptools import setup, find_packages
import sys
import os
version = "0.17"
if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()
if sys.argv[-1] == 'zip':
    os.system("python setup.py sdist --formats=zip")
    sys.exit()
setup(
    name="aces",
    version=version,
    description="A python framework for computational physics numerical experiments.",
    author="Yang Zhou",
    author_email="404422239@qq.com",
    url="https://github.com/vanceeasleaf/aces",
    license="GPL2.0",
    packages=find_packages(),
    scripts=["scripts/ae"]
    # long_description=open('README.md').read()
)
