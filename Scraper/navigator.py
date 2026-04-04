from Scraper.parser import Judge
import constants as c
import asyncio
import time

##########################################################################
# Defining what will be added:  
# 1: Button Prioritization (based on name)
# 2: Link Prioritization
# 3: Location rework + update usage
# 4: Check for Dead Ends
# 5: Save Websites Scores (from Judge)
# 6: Add Capabilities to handle search bars
# 7: Add Abilities to return to the previous website with the best score

class Navigator:
    # Class which uses Playwright in order to navigate the internet and get html data to be used by the parser

    def __init__(self, page):

        self.page = page
        self.locations = []
        if self.page.url != "about:blank":
            self.locations.append(self.page.url)
        self.page.on("request", self.update_request_time)
        self.window_start = time.time()
        self.num_requests = 0
        self.delay = False

    async def update_request_time(self):
        # Tracks the number of request being made to ensure it does not go over the rate limit

        self.num_requests += 1
        print(f"Num Requests: {self.num_requests} | Time Window: {time.time() - self.window_start}")
        if self.num_requests >= c.REQUEST_LIMIT:
            await self.wait_for_reset()

        await self.request_reset()

    async def request_reset(self):
        # Function Which resets the request counter when the time runs out

        if time.time() - self.window_start < c.LIMIT_WINDOW:
            return

        self.num_requests = 0
        self.window_start = time.time() - ((time.time() - self.window_start) - c.LIMIT_WINDOW)
    
    async def wait_for_reset(self):
        # Function which waits until the current time window ends, stopping all requests until a new window has started
        print("Sleeping, zzzzzzzzzzzzzzzzz")
        self.delay = True
        await asyncio.sleep(c.LIMIT_WINDOW - (time.time() - self.window_start))
        self.delay = False

    # Function which uses playwright to access static html
    async def get_html(self):
        # Loads the dom content of a page when the page has loaded its dom content

        await self.page.wait_for_load_state("domcontentloaded")
        html = await self.page.content()
        return html
    
    async def wait_for_delay(self):
        # Function used to have every other function to wait until the rate delay is over

        if not self.delay:
            return
        while self.delay:
            await asyncio.sleep(0.2)
    
    async def goto(self, url):
        # Goes to a new url, saving the url to the locations list
        w = await self.wait_for_delay()
        try: 
            await self.page.goto(url)
        except Exception as e:
            return False
        self.locations.append(url)
        return True

    async def mouse_scroll(self, length):
        # Uses the mouse from playwright in order to scroll down a page length pixels
        move_len = length // c.NUM_MOUSE_SCROLLS
        for _ in range(c.NUM_MOUSE_SCROLLS):
            w = await self.wait_for_delay()
            await self.page.mouse.wheel(0, move_len)
            await asyncio.sleep(0.1)

    async def instant_scroll(self):
        # Instantly scrolls down to the bottom of a page.
        w = await self.wait_for_delay()
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    async def infinite_scroll(self, max_scrolls=None):
        # Scrolls an infinite scrolling page until it reaches the bottom or max scrolls is reached.
        # Note: This function has yet to be tested due to a lack of any site to test yet.
        # It will be tested on a later date (whenever I feel like it)

        old_height = await self.page.evaluate("document.body.scrollHeight")
        new_height = old_height
        scroll_length = await self.page.evaluate("window.innerHeight") * 2
        num_scrolls = 0
        no_count = 0

        # Scrolls the entire height of the webpage once so content is ensured to load.
        await self.mouse_scroll(old_height)
        await asyncio.sleep(1)

        while True:
            await self.mouse_scroll(scroll_length * 2)
            num_scrolls += 1
            await asyncio.sleep(1)
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height ==  old_height:
                no_count += 1
                if no_count >= 2:
                    break
            if max_scrolls is not None:
                if max_scrolls < num_scrolls:
                    break
            old_height = new_height

    async def return_to_idx(self, idx):
        # Returns the page to a preivious url based off of its location in the locations list
        await self.page.goto(self.locations[idx])

    async def get_all_buttons(self):
        # Returns a list of all the buttons contained within the page.
        buttons = await self.page.get_by_role("button").all()
        return buttons

    async def get_all_links(self):
        # Returns a list of all the links contained within the page.
        links = await self.page.get_by_role("link").all()
        return links
    
    async def click_all(self, button=True):
        # Clicks on all of the buttons or links and checks for the changes in the website.
        w = await self.wait_for_delay()
        previous_page = self.locations[len(self.locations) - 1]
        if button:
            clickables = await self.get_all_buttons()
        else:
            clickables = await self.get_all_links()

        for clickable in clickables:
            await clickable.click()
            await asyncio.sleep(.25)
            print("Button Clicked")
            # Insert function which checks smth (will be added later once the parser is ready)
            if self.page.url != previous_page:
                await asyncio.sleep(.25)
                self.locations.append(self.page.url)
                await self.goto(previous_page)

    async def harvest_data(self, parser):
        # This Function will be altered in order to work for multiple websites (or get deleted)
        w = await self.wait_for_delay()
        total_data = []

        collecting_data = True
        while collecting_data:
            html = await self.get_html()
            data, new_url = await asyncio.to_thread(parser.parse_through_quotes, html, self.locations[0])
            if new_url is None:
                collecting_data = False
            else:
                await self.goto(new_url)
            if len(total_data) > c.BATCH_SIZE:
                collecting_data = False
            total_data += data

        return total_data


class Analyzer(Navigator):
    # This class is focused on getting information about the page

    def __init__(self, page):
        super().__init__(page)
        judge = Judge()
        scraping_score = []
        exploraton_score = []

    async def get_all_buttons(self):
        buttons = await super().get_all_buttons()
        prioritized_list = []
        for button in buttons:
            if any(priority in button.inner_text() for priority in c.MAX_PRIORITY):
                prioritized_list.append(button)
        
        for button in buttons:
            if any(priority in button.inner_text() for priority in c.NORMAL_PRIORITY):
                prioritized_list.append(button)
        
        for button in buttons:
            if any(button == b for b in prioritized_list):
                continue
            if not any(reject in button.inner_text() for reject in c.REJECT):
                prioritized_list.append(button)

        return prioritized_list

    async def check_infinite_scroll(self):
        old_height = await self.page.evaluate("document.body.scrollHeight")
        await self.mouse_scroll(old_height)
        new_height = await self.page.evaluate("document.body.scrollHeight")
        await asyncio.sleep(0.5)
        if new_height > old_height:
            return True
        return False


class Explorer(Analyzer):
    pass