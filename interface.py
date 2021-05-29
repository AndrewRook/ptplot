


if __name__ == "__main__":
    import pandas as pd
    test = pd.DataFrame({"one": [1, 2, 3, 4], "two": [5, 6, 7, 8]})
    fig = PTPlot(data=test) + NFLField() + NFLTeams() + Animation(
        frame_column="frame", timestamp_column="timestamp", timestamp_format="%H:%m:%s"
    ) + plot_positions(x="x", y="y") + plot_tracks(x="x", y="y", filter_on="")