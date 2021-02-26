# ptplot
`ptplot` makes it easy to turn player-tracking data into beautiful,
interactive visualizations — including animations! These visualizations can be used to guide
data exploration/analysis work, or to embed in webpages to share with
the world. 

## Installation

`ptplot` can be installed via pip:

```bash
$ pip install ptplot
```

It is strongly recommended that you install `ptplot` into a virtual
environment, such as with [`conda`](https://docs.conda.io/en/latest/):

```bash
[After installing conda]
$ conda create -n player_tracking python=3
$ conda activate player_tracking
$ pip install ptplot
```

You may wish to install some of `ptplot`'s dependencies
via conda, specifically `pandas` and `plotly`:

```bash
[After installing conda]
$ conda create -n player_tracking python=3 pandas plotly
$ conda activate player_tracking
$ pip install ptplot
```

## Getting Started

Making your first plot can be as simple as

```python
import pandas as pd
from ptplot import plotting
data = pd.read_csv([YOUR PLAYER TRACKING DATA])
fig = plotting.animate_positions(
    data, "x", "y", "frame"
)
fig.show()
```

For additional documentation and examples, check out the
notebooks in the `notebooks/` directory. 