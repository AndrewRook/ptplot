# Developing on `ptplot`

## Installation

Install either with pip using the `[dev]` extras or via the conda
environment file:
```bash
$ pip install ptplot[dev]
--OR (Note that this will create your conda env for you)--
$ conda env create -f environment.yml
```

## Running tests and style checks

`ptplot` uses `pytest`, `flake8`, and `black`. All of these must
pass in order for a PR to be merged, so it's valuable to run them
yourself locally before pushing changes:

```bash
$ python -m pytest
$ python -m black -l 120 ptplot/
$ python -m flake8 ptplot/
```

## Notebooks

`ptplot`'s primary form of documentation is currently Jupyter 
notebooks. Unfortunately, due to how plotly renders animations,
the animation notebook is quite large in size. Whenever you
work with `ptplot` animations in the notebook, please check the
size of the resulting notebook **before** committing it to the repo.


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