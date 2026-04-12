# Beauty is in the eye of the beholder, and the beholder is blind.
# And so am I, as I gouged out my eyes due to this project...

from dearpygui import dearpygui as dpg
from playwright.async_api import async_playwright
from dearpygui_async import DearPyGuiAsync
from Scraper.navigator import Explorer
from Filters.bi_encoder import BiEncoder
from Filters.cross_encoder import CrossEncoding
from Filters.word_filter import WordFilter
from data_manager import DataManager
import constants as c
import asyncio
import utils
import copy

num_inputs = c.DEFAULT_INPUT
num_websites = c.DEFAULT_WEBSITES
user_inputs = ["", "", "", "", "", "", "", "", "", ""]
websites = [c.DEFAULT_WEBSITE_1, c.DEFAULT_WEBSITE_2, c.DEFAULT_WEBSITE_3, "", "", "", "", "", "", ""]
started = False
num_samples = 0
page_processes = {}

dpg_async = DearPyGuiAsync()

def save_input(selector, app_data):
    idx = int(selector.replace(c.SAMPLE_FILTER + "_", ""))
    user_inputs[idx] = app_data


def delete_previous_input():
    dpg.delete_item(c.SAMPLE_FILTER)
    for i in range(num_inputs):
        dpg.delete_item(c.SAMPLE_FILTER + "_" + str(i))


def update_websites(sender, appdata):
    global num_websites
    save_websites()
    destroy_website_inputs()
    num_websites = appdata
    create_website_input()


def save_websites():
    for i in range(num_websites):
        website = dpg.get_value(c.WEBSITE_INPUT_TAG + "_" + str(i))
        websites[i] = website


def destroy_website_inputs():
    for i in range(num_websites):
        if dpg.does_item_exist(c.WEBSITE_INPUT_TAG + "_" + str(i)):
            dpg.delete_item(c.WEBSITE_INPUT_TAG + "_" + str(i))


def create_website_input():
    for i in range(num_websites):
        dpg.add_input_text(
            label="Website",
            tag=c.WEBSITE_INPUT_TAG + "_" + str(i),
            default_value=websites[i],
            parent=c.OPTION_WINDOW_TAG,
            before=c.SUBMIT_TEXT_TAG
        )


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

    can_start = True

    for i in range(num_inputs):
        if dpg.get_value(c.SAMPLE_FILTER + "_" + str(i)) == "":
            can_start = False

    if dpg.get_value(c.FILE_NAME_TAG) == "" or " " in dpg.get_value(c.FILE_NAME_TAG):
        can_start = False

    w = WordFilter(dpg.get_value(c.WORD_FILTER))
    if not dpg.get_value(c.WORD_FILTER).lower() == "none" and w.words is None:
        can_start = False

    return can_start


async def display_failure():
    if not dpg.does_item_exist(c.FAILED_TAG):
        dpg.add_text("Cannot start as some options have not been filled out...", parent=c.OPTION_WINDOW_TAG, before=c.SUBMIT_TAG, tag=c.FAILED_TAG)
    dpg.set_item_label(c.SUBMIT_TAG, "Submit - Failed")


def create_website_table():
    with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, resizable=True, no_host_extendX=True, borders_innerV=True,
              borders_outerV=True, borders_outerH=True, tag=c.WEBSITE_TABLE_TAG, parent=c.DISPLAY_WINDOW_TAG):
        num_columns = 0
        for keys in page_processes:
            dpg.add_table_column(label=keys)
            num_columns += 1
        for i in range(0, 3):
            with dpg.table_row():
                for process in page_processes.values():
                    dpg.add_text(process[i])


async def update_table():
    original_process = copy.deepcopy(page_processes)
    while True:
        await asyncio.sleep(1)
        if original_process == page_processes:
            # print(f"Original: {original_process} | new: {page_processes}")
            continue
        original_process = copy.deepcopy(page_processes)
        dpg.delete_item(c.WEBSITE_TABLE_TAG)
        create_website_table()


def create_sample_graph(samples, times, goal):
    with dpg.plot(label="Samples", height=400, width=400, tag=c.GRAPH_TAG, parent=c.DISPLAY_WINDOW_TAG, before=c.WEBSITE_TABLE_TAG):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)", tag=c.X_AXIS)
        dpg.add_plot_axis(dpg.mvYAxis, label="Samples", tag=c.COLLECTED_SAMPLES_AXIS_TAG)

        dpg.add_line_series(times, samples, label="Collected Samples", parent=c.COLLECTED_SAMPLES_AXIS_TAG, tag=c.SERIES_ONE)
        dpg.add_line_series(times, utils.create_list_of_num(len(times), goal), label="Goal", parent=c.COLLECTED_SAMPLES_AXIS_TAG, tag=c.SERIES_TWO)
    print("End")


async def manage_graphs(goal):
    time_sequence = [0]
    sample_sequence = [0]
    current_time = 0
    print("Started")
    while True:
        print("Updated")
        await asyncio.sleep(1)
        current_time += 1
        time_sequence.append(current_time)
        sample_sequence.append(num_samples)
        dpg.set_value(c.SERIES_ONE, (time_sequence, sample_sequence))
        dpg.set_value(c.SERIES_TWO, (time_sequence, utils.create_list_of_num(len(time_sequence), goal)))
        dpg.fit_axis_data(c.X_AXIS)
        dpg.fit_axis_data(c.COLLECTED_SAMPLES_AXIS_TAG)


def print_process(sender, appdata):
    for url, process in page_processes.items():
        print(f"Page: {url} | Processe: {process}")
    print(f"Samples: {num_samples}")


async def start(sender, app_data):
    # Core function which runs the scraping and processing of data. 

    # Check if the process can begin
    global started, num_samples, page_processes
    if not await can_start():
        await display_failure()
        return
    dpg.hide_item(c.OPTION_WINDOW_TAG)

    # Option variables to be used later
    save_websites()
    filter_value = dpg.get_value(c.SIMILARITY_SELECT_TAG)
    file_type = dpg.get_value(c.FILE_SELECT_TAG)
    sample_number = dpg.get_value(c.SAMPLE_TAG)
    overflow = dpg.get_value(c.OVERFLOW_SELECT_TAG)  # Has yet to be implemented
    save_name = dpg.get_value(c.FILE_NAME_TAG)
    words = dpg.get_value(c.WORD_FILTER)
    text = user_inputs[: num_inputs]
    websites_to_scrape = websites[: num_websites]
    num_required_samples = sample_number + sample_number * overflow
    page_processes = {"Website": ["Scraping", "Exploring", "Sleeping"]}
    for i in range(len(websites_to_scrape)):
        page_processes[websites_to_scrape[i]] = [False, False, False]
    create_website_table()
    table_task = asyncio.create_task(update_table())
    create_sample_graph([0], [0], num_required_samples)
    graph_task = asyncio.create_task(manage_graphs(num_required_samples))
    data = []

    # Scraping
    bi_encoder = await asyncio.to_thread(BiEncoder, text, filter_value)
    w = WordFilter(words)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel=c.BROWSER, headless=c.HEADLESS)
        scrape_call = []
        navs = []
        for website in websites_to_scrape:
            page = await browser.new_page()
            process = page_processes[website]
            nav = Explorer(page, process, [], text)
            works = await nav.goto(website)
            if not works:
                await display_failure()
                await browser.close()
                dpg.show_item(c.OPTION_WINDOW_TAG)
                table_task.cancel()
                graph_task.cancel()
                return
            scrape_call.append(nav.get_samples(sample_number//num_websites))
            navs.append(nav)

        while len(data) < num_required_samples:
            samples = []
            s = await asyncio.gather(*tuple(scrape_call))
            for sample in s:
                samples += sample
                num_samples += len(sample[0])
            scrape_call = []

            word_list = []
            if w.words is not None:
                for part in samples:
                    if await asyncio.to_thread(w.evaluate, w.words, part[0]):
                        word_list.append(part)
            new_list = []
            for part in word_list:
                if await asyncio.to_thread(bi_encoder.evaluate_text, part[0]):
                    new_list.append(part[0])
            data += new_list

            for nav in navs:
                scrape_call.append(nav.get_samples(sample_number//num_websites)) 
    
    if sample_number < len(data):
        cross_encoder = await asyncio.to_thread(CrossEncoding, text)
        c_list = await asyncio.to_thread(cross_encoder.get_comparison_list, data)
        idx_list = await asyncio.to_thread(utils.get_max_indexes, c_list, sample_number) 
        final_list = []
        for idx in idx_list:
            final_list.append(new_list[idx])
    else:
        final_list = data

    dm = DataManager(final_list, name=save_name)
    await asyncio.to_thread(dm.save_data, file_type)
    dpg.add_text("Data Has been Saved!!!", parent=c.DISPLAY_WINDOW_TAG)


if __name__ == "__main__":

    dpg.create_context()
    dpg.create_viewport(title="Data Eater", width=800, height=700)

    with dpg.window(label="Display", width=800, height=700, tag=c.DISPLAY_WINDOW_TAG):
        dpg.add_text("Display")
        dpg.add_button(label="Test", callback=print_process)

    with dpg.window(label="Select", width=800, height=700, tag=c.OPTION_WINDOW_TAG):

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

        # File Name
        dpg.add_text("Select what you wish to name the file in which the scraped data is saved")
        dpg.add_input_text(label="Data File Name", tag=c.FILE_NAME_TAG)

        # Website Selection
        dpg.add_text("Select which websites you which to scrape, or use these here default websites")
        dpg.add_input_int(
            label="Number of Websites", 
            tag=c.NUM_WEBSITE_TAG, 
            min_clamped=True, 
            min_value=c.MIN_WEBSITES, 
            max_clamped=True, 
            max_value=c.MAX_WEBSITES, 
            default_value=c.DEFAULT_WEBSITES,
            callback=update_websites
        )

        # Set up submit button (hard af)
        dpg.add_text("Click the button below to submit and start the data collection process", tag=c.SUBMIT_TEXT_TAG)
        dpg.add_button(label="Submit", tag=c.SUBMIT_TAG, callback=start)

        # Set up Filter Inputs
        set_up_input()
        create_website_input()


    dpg.setup_dearpygui()
    dpg.show_viewport()

    dpg_async.run()

    dpg.destroy_context()