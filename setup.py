#!/usr/bin/env python

"""The setup script."""
import versioneer
import parse_envs

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

extras = {
    'dev': [
        'black','notebook', 'flake8', 'mypy', 'pytest', 'pytest-cov', 'tox'
    ]
}

requirements, extra_requirements = parse_envs.parse_conda_envs(
    "environment_minimum_requirements.yml",
    "environment.yml",
    optional_packages=extras
)

setup(
    author='Andrew Schechtman-Rook',
    author_email='footballastronomer@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    cmdclass=versioneer.get_cmdclass(),
    description='Make beautiful plots of player tracking data',
    extras_require=extra_requirements,
    install_requires=requirements,
    license='GNU General Public License v3',
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='ptplot',
    name='ptplot',
    packages=find_packages(include=['ptplot', 'ptplot.*']),
    url='https://github.com/AndrewRook/ptplot',
    version=versioneer.get_version(),
    zip_safe=False,
)
