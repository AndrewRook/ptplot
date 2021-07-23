FIND_CURRENT_FRAME = """
var data = source.data;
var filter = view.filters[0];
var indices = [];

for (let i = 0; i < data[frame_column].length; i++) {
    if (data[frame_column][i] == cb_obj.value) {
        indices.push(i);
    }
    // Assumes data is sorted by frame_column
    if (data[frame_column][i] > cb_obj.value) {
        break;
    }
}

filter.indices = indices;
source.change.emit();
"""
FIND_ALL_FRAMES_UP_TO_CURRENT_FRAME = """
var data = source.data;
var full_data = full_source.data
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
