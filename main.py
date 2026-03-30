from dearpygui import dearpygui as dpg
from playwright.async_api import async_playwright
from dearpygui_async import DearPyGuiAsync
from Scraper.navigator import Navigator
from Scraper.parser import Parser
from Filters.bi_encoder import BiEncoder
from Filters.cross_encoder import CrossEncoding
from data_manager import DataManager
import constants as c
import asyncio
import utils

num_inputs = c.DEFAULT_INPUT
user_inputs = ["", "", "", "", "", "", "", "", "", ""]
started = False

dpg_async = DearPyGuiAsync()

def save_input(selector, app_data):
    idx = int(selector.replace(c.SAMPLE_FILTER + "_", ""))
    user_inputs[idx] = app_data


def delete_previous_input():
    dpg.delete_item(c.SAMPLE_FILTER)
    for i in range(num_inputs):
        dpg.delete_item(c.SAMPLE_FILTER + "_" + str(i))


def set_up_input():
    # Sets up the user input for filtering text for samples

    dpg.add_input_int(
        label="Number of samples you wish to use", 
        tag=c.SAMPLE_FILTER, 
        default_value=num_inputs, 
        min_value=c.MIN_INPUT, 
        max_value=c.MAX_INPUT, 
        min_clamped=True,
        max_clamped=True,
        parent=c.OPTION_WINDOW_TAG,
        callback=update_inputs,
        before=c.WORD_FILTER_TEXT
    )

    for i in range(num_inputs):
        dpg.add_input_text(
            label="sample Input", 
            tag=c.SAMPLE_FILTER + "_" + str(i), 
            parent=c.OPTION_WINDOW_TAG,
            callback=save_input,
            default_value=user_inputs[i],
            before=c.WORD_FILTER_TEXT
        )


def update_inputs(sender, appdata):
    # Recreated the input screen everytime the thing is updates
    global num_inputs
    delete_previous_input()
    num_inputs = appdata
    set_up_input()

async def can_start():
    # Checks if the start function is allowed to start

    for i in range(num_inputs):
        if dpg.get_value(c.SAMPLE_FILTER + "_" + str(i)) == "":
            return False
    return True


async def start(sender, app_data):
    # Core function which runs the scraping and processing of data. 

    # Check if the process can begin
    global started
    if not await can_start():
        if not dpg.does_item_exist(c.FAILED_TAG):
            dpg.add_text("Cannot start as some options have not been filled out...", parent=c.OPTION_WINDOW_TAG, before=c.SUBMIT_TAG, tag=c.FAILED_TAG)
        dpg.set_item_label(c.SUBMIT_TAG, "Submit - Failed")
        return
    
    # Option variables to be used later
    filter_value = dpg.get_value(c.SIMILARITY_SELECT_TAG)
    file_type = dpg.get_value(c.FILE_SELECT_TAG)
    sample_number = dpg.get_value(c.SAMPLE_TAG)
    overflow = dpg.get_value(c.OVERFLOW_SELECT_TAG)  # Has yet to be implemented
    text = user_inputs[: num_inputs]

    # Delete the option window, as it is no longer needed
    dpg.delete_item(c.OPTION_WINDOW_TAG)

    # Scraping
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel=c.BROWSER, headless=c.HEADLESS)
        page = await browser.new_page()
        await page.goto("https://quotes.toscrape.com")
        nav = Navigator(page)
        parser = Parser()
        data = await nav.harvest_data(parser)
    
    bi_encoder = await asyncio.to_thread(BiEncoder, text, filter_value) 
    new_list = []
    for part in data:
        if await asyncio.to_thread(bi_encoder.evaluate_text, part[0]):
            new_list.append(part[0])
    
    if sample_number < len(new_list):
        cross_encoder = await asyncio.to_thread(CrossEncoding, text)
        c_list = await asyncio.to_thread(cross_encoder.get_comparison_list, new_list)
        idx_list = await asyncio.to_thread(utils.get_max_indexes, c_list, sample_number) 
        final_list = []
        for idx in idx_list:
            final_list.append(new_list[idx])
    else:
        final_list = new_list
    
    dm = DataManager(final_list)
    await asyncio.to_thread(dm.save_data, file_type) # dm.save_data(file_type)
    dpg.add_text("Data Has been Saved!!!", parent=c.DISPLAY_WINDOW_TAG)


if __name__ == "__main__":

    dpg.create_context()
    dpg.create_viewport(title="Data Eater", width=800, height=600)

    with dpg.window(label="Display", width=800, height=600, tag=c.DISPLAY_WINDOW_TAG):
        dpg.add_text("Display")
        dpg.add_button(label="Test")

    with dpg.window(label="Select", width=800, height=600, tag=c.OPTION_WINDOW_TAG):

        # Filter Selection
        dpg.add_text("Select options for scraping")

        # Filter input
        dpg.add_text("Below type in each value you want to filter your dataset with", tag=c.FILTER_TEXT_TAG)

        # Simple Word Filter
        dpg.add_text("Below, type in the words you want to include or exclude, (type NONE if you wish to have no word filter)", tag=c.WORD_FILTER_TEXT)
        dpg.add_input_text(label="Word Filter", tag=c.WORD_FILTER, default_value=c.DEFAULT_WORD_TEXT)

        # Dataset Sample
        dpg.add_text("Select the number of samples to be in the final dataset", tag=c.SAMPLE_TEXT_TAG)
        dpg.add_input_int(label="Sample Number", step=c.NUM_SAMPLE_STEPS, tag=c.SAMPLE_TAG, min_value=c.MIN_SAMPLE, min_clamped=True, default_value=c.DEFAULT_SAMPLE)

        # Dataset Overflow
        dpg.add_text("Select the amount of overflow samples")
        dpg.add_input_int(label="Overflow", tag=c.OVERFLOW_SELECT_TAG, min_value=c.MIN_OVERFLOW, min_clamped=True, max_value=c.MAX_OVERFLOW, max_clamped=True, default_value=c.DEFAULT_OVERFLOW)

        # Similarity to Samples
        dpg.add_text("Input the minimum similarity between your sample and a different text in order for that text to be included in the sample",tag=c.SIMILARITY_TEXT_TAG)
        dpg.add_slider_float(label="Similarity", tag=c.SIMILARITY_SELECT_TAG, default_value=c.DEFAULT_BI, min_value=c.MIN_BI, max_value=c.MAX_BI)

        # File Selection
        dpg.add_text("Select which file type you wish to save your data in", tag=c.FILE_TEXT_TAG)
        dpg.add_radio_button(label="File Type", items=["CSV", "Parquet", "JSONL", "SQLite"], default_value="CSV", tag=c.FILE_SELECT_TAG)

        dpg.add_text("Click the button below to submit and start the data collection process")
        dpg.add_button(label="Submit", tag=c.SUBMIT_TAG, callback=start)

        # Set up Filter Inputs
        set_up_input()


    dpg.setup_dearpygui()
    dpg.show_viewport()

    dpg_async.run()

    dpg.destroy_context()