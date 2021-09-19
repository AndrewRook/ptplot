# Developing on `ptplot`

## Installation

Install either with the conda
environment file (strongly recommended) or via pip using the `[dev]` extras:
```bash
--This uses ssh to clone the repo, feel free to use your protocol of choice--
$ git clone git@github.com:AndrewRook/ptplot.git
$ cd ptplot 
$ conda env create -f environment.yml
$ conda activate ptplot-dev
$ pip install -e .
--OR (Note that you will need to separately install nodejs)--
$ pip install -e .[dev]
```

## Running tests and style checks

`ptplot` uses `pytest`, `flake8`, `mypy`, and `black`. All of these must
pass in order for a PR to be merged, so it's valuable to run them
yourself locally before pushing changes:

```bash
$ python -m mypy --exclude ptplot/_version.py ptplot/ 
$ python -m pytest tests/ ptplot/
$ python -m black -l 120 ptplot/
$ python -m flake8 ptplot/
```

## Notebooks

`ptplot`'s primary form of documentation is currently Jupyter 
notebooks. Unfortunately, due to how plotly renders animations,
the animation notebook is quite large in size. Whenever you
work with `ptplot` animations in the notebook, please check the
size of the resulting notebook **before** committing it to the repo.

_Note: When you make an update to any of the custom extensions, you may
need to [force-reload the notebook pages](https://support.google.com/chrome/thread/16531954/clear-cache-for-specific-website-in-google-chrome?hl=en) in order to clear the cache and
make Jupyter look for the new JS files._


## Cutting a release

1. Make sure that all changes you want have been merged to `main`.
2. Rerun all the notebooks and make sure they still work. If the
results have changed in any way, make sure that's reflected in the
versions that are in `main`. If not, rerun them and PR those updates
in.
3. In GitHub, create a [new release](https://github.com/AndrewRook/ptplot/releases/new)
based on the `main` branch.
Give it a version tag that makes sense. `ptplot` uses [semantic
versioning](https://semver.org/), with no "v" preceding the
version numbers. 
4. Go to the Actions tab for the repo and confirm that the publish
action runs successfully (takes a couple of minutes). 