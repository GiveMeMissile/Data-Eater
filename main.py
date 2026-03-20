from dearpygui import dearpygui as dpg
import constants as c
import asyncio
from playwright.async_api import async_playwright

# Options to be added:
# Filter Selection ✔
# Filter Slider ✔
# Filter Input ✔
# File Selection ✔
# Bi Encoding Confidence ✔
# Number of Samples ✔
# OverFlow Samples ✔

num_inputs = c.DEFAULT_INPUT
input_name = c.FILTER_OPTION_2
user_inputs = ["", "", "", "", "", "", "", "", "", ""]
started = False


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
    if dpg.does_item_exist(c.SIMILARITY_TEXT_TAG):
        dpg.delete_item(c.SIMILARITY_TEXT_TAG)
    if dpg.does_item_exist(c.SIMILARITY_SELECT_TAG):
        dpg.delete_item(c.SIMILARITY_SELECT_TAG)


def set_up_input():
    dpg.add_input_int(
        label="Number of " + input_name + "s you wish to use", 
        tag=input_name, 
        default_value=num_inputs, 
        min_value=c.MIN_INPUT, 
        max_value=c.MAX_INPUT, 
        min_clamped=True,
        max_clamped=True,
        parent=c.OPTION_WINDOW_TAG,
        callback=update_inputs,
        before=c.SAMPLE_TEXT_TAG
    )

    for i in range(num_inputs):
        dpg.add_input_text(
            label=input_name + " Input", 
            tag=input_name + "_" + str(i), 
            parent=c.OPTION_WINDOW_TAG,
            callback=save_input,
            default_value=user_inputs[i],
            before=c.SAMPLE_TEXT_TAG
        )
    
    if input_name == "Sample":
        dpg.add_text(
            "Input the minimum similarity between your sample and a different text in order for that text to be included in the sample",
            tag=c.SIMILARITY_TEXT_TAG,
            parent=c.OPTION_WINDOW_TAG,
            before=c.FILE_TEXT_TAG
        )
        dpg.add_slider_float(
            label="Similarity",
            tag=c.SIMILARITY_SELECT_TAG,
            parent=c.OPTION_WINDOW_TAG,
            default_value=c.DEFAULT_BI,
            before=c.FILE_TEXT_TAG,
            min_value=c.MIN_BI,
            max_value=c.MAX_BI
        )


def update_inputs(selector, app_data):
    global num_inputs
    delete_previous_input()
    num_inputs = app_data
    set_up_input()


def can_start():
    for i in range(num_inputs):
        if dpg.get_value(input_name + "_" + str(i)) == "":
            return False
    return True


def start():
    global started
    if not can_start():
        dpg.add_text("Cannot start as some options have not been filled out...", parent=c.OPTION_WINDOW_TAG, before=c.SUBMIT_TAG, tag=c.FAILED_TAG)
        dpg.set_item_label(c.SUBMIT_TAG, "Submit - Failed")
        return
    dpg.delete_item(c.OPTION_WINDOW_TAG)
    started = True


if __name__ == "__main__":

    dpg.create_context()
    dpg.create_viewport(width=800, height=500)

    with dpg.window(label="Display", width=800, height=400, tag=c.DISPLAY_WINDOW_TAG):
        dpg.add_text("Display")

    with dpg.window(label="Select", width=800, height=400, tag=c.OPTION_WINDOW_TAG):

        # Filter Selection
        dpg.add_text("Select options for scraping")
        dpg.add_text("Select which filter is going to be used")
        dpg.add_radio_button(label="Filter", items=[c.FILTER_OPTION_1, c.FILTER_OPTION_2], tag=c.FILTER_SELECT_TAG, default_value=input_name, callback=input_option)

        # Filter input
        dpg.add_text("Below type in each value you want to filter your dataset with", tag=c.FILTER_TEXT_TAG)

        # Dataset Sample
        dpg.add_text("Select the number of samples to be in the final dataset", tag=c.SAMPLE_TEXT_TAG)
        dpg.add_input_int(label="Sample Number", step=c.NUM_SAMPLE_STEPS, tag=c.SAMPLE_TAG, min_value=c.MIN_SAMPLE, min_clamped=True, default_value=c.DEFAULT_SAMPLE)

        # Dataset Overflow
        dpg.add_text("Select the amount of overflow samples")
        dpg.add_input_int(label="Overflow", tag=c.OVERFLOW_SELECT_TAG, min_value=c.MIN_OVERFLOW, min_clamped=True, max_value=c.MAX_OVERFLOW, max_clamped=True, default_value=c.DEFAULT_OVERFLOW)

        # File Selection
        dpg.add_text("Select which file type you wish to save your data in", tag=c.FILE_TEXT_TAG)
        dpg.add_radio_button(label="File Type", items=["CSV", "Parquet", "JSONL", "SQLite"], default_value="CSV", tag=c.FILE_SELECT_TAG)

        dpg.add_text("Click the button below to submit and start the data collection process")
        dpg.add_button(label="Submit", tag=c.SUBMIT_TAG, callback=start)

        # Set up Filter Inputs
        set_up_input()


    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        # Will be used for display later
        dpg.render_dearpygui_frame()

    dpg.destroy_context()