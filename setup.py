#!/usr/bin/env python

"""The setup script."""
import versioneer

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

# TODO: Coordinate with environment.yml
requirements = [
    'dask==2021.1.0',
    'numpy==1.19.5',
    'pandas==1.2.0',
    'plotly==4.14.3',
    'svgpathtools==1.4.1'
    'versioneer=0.19'
]

dev_packages = ['flake8==3.8.4', 'pytest==6.2.1', 'pytest-cov==2.11.1']

extra_requirements = {'dev': dev_packages}

setup(
    author="Andrew Schechtman-Rook",
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
    description="Make beautiful plots of player tracking data",
    extras_require=extra_requirements,
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme,
    include_package_data=True,
    keywords='ptplot',
    name='ptplot',
    packages=find_packages(include=['ptplot', 'ptplot.*']),
    url='https://github.com/AndrewRook/ptplot',
    version=versioneer.get_version(),
    zip_safe=False,
)
