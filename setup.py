#!/usr/bin/env python
from codecs import open

from setuptools import find_packages, setup


def readme():
    with open("README.md", "r") as infile:
        return infile.read()


classifiers = [
    # Pick your license as you wish (should match "license" above)
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
]
setup(
    name="drf-typed-views",
    version="0.3.0",
    description="Use type annotations for automatic request validation in Django REST Framework",
    author="Robert Singer",
    author_email="robertgsinger@gmail.com",
    packages=find_packages(exclude=["test_project*"]),
    url="https://github.com/rsinger86/drf-typed-views",
    license="MIT",
    keywords="django rest type annotations automatic validation validate",
    long_description=readme(),
    classifiers=classifiers,
    long_description_content_type="text/markdown",
)
