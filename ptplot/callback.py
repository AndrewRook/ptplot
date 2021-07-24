# This can also be done via setting an IndexFilter view on the data and then updating the indices
# of that filter. This is actually how it works in 0.2.0. However there is a bug when trying
# to animate a single object (https://github.com/bokeh/bokeh/issues/11439) so for
# the time being this is the best way to do it :/
FIND_CURRENT_FRAME = """
var data = source.data;
var full_data = full_source.data;
for (const column in data) {
    data[column] = [];
    for (let i = 0; i < full_data[frame_column].length; i++) {
        if (full_data[frame_column][i] == cb_obj.value) {
            data[column].push(full_data[column][i]);
        }
        // Assumes data is sorted by frame_column
        if (full_data[frame_column][i] > cb_obj.value) {
            break;
        }
    }
}
source.change.emit();
"""

FIND_ALL_FRAMES_UP_TO_CURRENT_FRAME = """
var data = source.data;
var full_data = full_source.data;
for (const column in data) {
    data[column] = [];
    for (let i = 0; i < full_data[frame_column].length; i++) {
        if (full_data[frame_column][i] <= cb_obj.value) {
            data[column].push(full_data[column][i]);
        }
        // Assumes data is sorted by frame_column
        if (full_data[frame_column][i] > cb_obj.value) {
            break;
        }
    }
}
source.change.emit();
"""
