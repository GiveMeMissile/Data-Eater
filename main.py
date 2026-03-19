from dearpygui import dearpygui as dpg

# Options to be added:
# Filter Selection ✔
# Filter Slider ✔
# Filter Input ✔
# File Selection ✔
# Bi Encoding Confidence ✔
# Number of Samples ✔
# OverFlow Samples ✔

OPTION_WINDOW = "select"
MIN_INPUT = 1
MAX_INPUT = 10
num_inputs = 3
input_name = "Word"
user_inputs = ["", "", "", "", "", "", "", "", "", ""]


def save_input(selector, app_data):
    idx = int(selector.replace(input_name + "_", ""))
    user_inputs[idx] = app_data


def input_option(selector, app_data):
    global input_name
    delete_previous_input()
    input_name = app_data
    set_up_input()


def delete_previous_input():
    dpg.delete_item(input_name)
    for i in range(num_inputs):
        dpg.delete_item(input_name + "_" + str(i))
    if dpg.does_item_exist("similarity_text"):
        dpg.delete_item("similarity_text")
    if dpg.does_item_exist("similarity"):
        dpg.delete_item("similarity")


def set_up_input():
    dpg.add_input_int(
        label="Number of " + input_name + "s you wish to use", 
        tag=input_name, 
        default_value=num_inputs, 
        min_value=MIN_INPUT, 
        max_value=MAX_INPUT, 
        min_clamped=True,
        max_clamped=True,
        parent=OPTION_WINDOW,
        callback=update_inputs,
        before="sample_num_text"
    )

    for i in range(num_inputs):
        dpg.add_input_text(
            label=input_name + " Input", 
            tag=input_name + "_" + str(i), 
            parent=OPTION_WINDOW,
            callback=save_input,
            default_value=user_inputs[i],
            before="sample_num_text"
        )
    
    if input_name == "Sample":
        dpg.add_text(
            "Input the minimum similarity between your sample and a different text in order for that text to be included in the sample",
            tag="similarity_text",
            parent=OPTION_WINDOW,
            before="file_text"
        )
        dpg.add_slider_float(
            label="Similarity",
            tag="similarity",
            parent=OPTION_WINDOW,
            default_value=0.5,
            before="file_text",
            min_value=0,
            max_value=1
        )


def update_inputs(selector, app_data):
    global num_inputs
    delete_previous_input()
    num_inputs = app_data
    set_up_input()


if __name__ == "__main__":

    dpg.create_context()
    dpg.create_viewport(width=800, height=500)

    with dpg.window(label="Select", width=800, height=400, tag=OPTION_WINDOW):

        # Filter Selection
        dpg.add_text("Select options for scraping")
        dpg.add_text("Select which filter is going to be used")
        dpg.add_radio_button(label="Filter", items=["Word", "Sample"], tag="filter", default_value=input_name, callback=input_option)

        # Filter input
        dpg.add_text("Below type in each value you want to filter your dataset with", tag="input_text")

        # Dataset Sample
        dpg.add_text("Select the number of samples to be in the final dataset", tag="sample_num_text")
        dpg.add_input_int(label="Sample Number", step=50, tag="sample_num", min_value=50, min_clamped=True, default_value=100)

        # Dataset Overflow
        dpg.add_text("Select the amount of overflow samples")
        dpg.add_input_int(label="Overflow", tag="overflow", min_value=1, min_clamped=True, max_value=10, max_clamped=True, default_value=3)

        # File Selection
        dpg.add_text("Select which file type you wish to save your data in", tag="file_text")
        dpg.add_radio_button(label="File Type", items=["CSV", "Parquet", "JSONL", "SQLite"], default_value="CSV", tag="file")

        # Set up Filter Inputs
        set_up_input()


    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        # Will be used for display later
        dpg.render_dearpygui_frame()

    dpg.destroy_context()