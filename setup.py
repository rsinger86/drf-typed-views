#!/usr/bin/env python
from setuptools import setup
from codecs import open


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
    version="0.1.0",
    description="Use type annotations for automatic request validation/sanitization.",
    author="Robert Singer",
    author_email="robertgsinger@gmail.com",
    packages=["rest_typed_views"],
    url="https://github.com/rsinger86/drf-typed-views",
    license="MIT",
    keywords="django rest type annotations automatic validation validate",
    long_description=readme(),
    classifiers=classifiers,
    long_description_content_type="text/markdown",
)
