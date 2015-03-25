import os

from setuptools import find_packages, setup


with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    long_description = readme.read()

classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy"
]

setup(
    name="cycy",
    packages=find_packages(),
    py_modules=(),
    setup_requires=["vcversioner"],
    vcversioner={"version_module_paths": ["cycy/__init__.py"]},
    author="Julian Berman",
    author_email="Julian@GrayVines.com",
    classifiers=classifiers,
    description="",
    license="MIT",
    long_description=long_description,
    url="",
)
