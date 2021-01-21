import plotly.graph_objects as go


def make_vline(y0, y1, x, **kwargs):
    """Make a vertical line of a defined distance."""
    return dict(
        type="line",
        y0=y0, y1=y1,
        x0=x, x1=x,
        **kwargs
    )


def make_hline(x0, x1, y, **kwargs):
    """Make a horizontal line of a defined distance."""
    return dict(
        type="line",
        y0=y, y1=y,
        x0=x0, x1=x1,
        **kwargs
    )


def create_field(figure=None):
    if figure is None:
        figure = go.Figure()

    # All units are in yards
    field_length = 120
    field_width = 53.3
    # First, make the field border:
    field_kwargs = {"line_width": 5, "line_color": "white"}
    field_border = [
        make_hline(0, field_length, 0, **field_kwargs),
        make_hline(0, field_length, field_width, **field_kwargs),
        make_vline(0, field_width, 0, **field_kwargs),
        make_vline(0, field_width, field_length, **field_kwargs)
    ]

    # Now make the yard and hash lines:
    line_kwargs = {"line_width": 2, "line_color": "white"}
    five_yard_lines = [
        make_vline(0, field_width, 5 * i, **line_kwargs)
        for i in range(2, 23)
    ]
    hash_width = 2 / 3 # Hashes are 2/3rds of a yard
    hash_length = 6 + 6/36 # six yards, six inches
    one_yard_lines = [
        make_vline(w, w + hash_width, i, **line_kwargs)
        for i in range(10, 111)
        if i % 10 != 0
        for w in [1, 23.58333, 23.58333 + hash_length - hash_width, 52.3 - hash_width]
    ]

    field_lines = field_border + five_yard_lines + one_yard_lines

    figure.update_layout(
        xaxis_showgrid=False, yaxis_showgrid=False,  # remove grid lines
        xaxis_zeroline=False, yaxis_zeroline=False,  # remove axis lines
        plot_bgcolor="green",  # set the background color
        yaxis_range=[-6, field_width + 6], xaxis_range=[-3, field_length + 3],  # set the range with a 2-yard buffer on each side
        width=800, height=500,
        shapes=field_lines
    )
    figure.update_xaxes(showticklabels=False)
    figure.update_yaxes(showticklabels=False)

    return figure
