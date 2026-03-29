from Scraper.parser import Judge
import constants as c
import asyncio
import time

############################
# Functions to be added:
# 1: Add Request Limit ✓
# 2: Scrolling Function ✓
# 3: Get All Buttons On a screen ✓
# 4: Get All links On a screen ✓

class Navigator:
    # Class which uses Playwright in order to navigate the internet and get html data to be used by the parser

    def __init__(self, page):

        self.judge = Judge()
        self.page = page
        self.locations = []
        if self.page.url != "about:blank":
            self.locations.append(self.page.url)
        self.page.on("request", self.update_request_time)
        self.window_start = time.time()
        self.num_requests = 0

    async def update_request_time(self):
        # Tracks the number of request being made to ensure it does not go over the rate limit

        self.num_requests += 1
        print(f"Num Requests: {self.num_requests} | Time Window: {time.time() - self.window_start}")
        if self.num_requests >= c.REQUEST_LIMIT:
            await self.wait_for_reset()

        await self.request_reset()

    async def request_reset(self):
        # Function Which resets the request counter when the time runs out

        if time.time() - self.window_start < 60:
            return

        self.num_requests = 0
        self.window_start = time.time() - (60 - (time.time() - self.window_start))
    
    async def wait_for_reset(self):
        # Function which waits until the current time window ends, stopping all requests until a new window has started
        print("Sleeping, zzzzzzzzzzzzzzzzz")
        time.sleep(60 - (time.time() - self.window_start))

    # Function which uses playwright to access static html
    async def get_html(self):
        # Loads the dom content of a page when the page has loaded its dom content

        await self.page.wait_for_load_state("domcontentloaded")
        html = await self.page.content()
        return html
    
    async def goto(self, url):
        # Goes to a new url, saving the url to the locations list
        await self.page.goto(url)
        self.locations.append(url)

    async def mouse_scroll(self, length):
        # Uses the mouse from playwright in order to scroll down a page length pixels
        move_len = length // c.NUM_MOUSE_SCROLLS
        for _ in range(c.NUM_MOUSE_SCROLLS):
            await self.page.mouse.wheel(0, move_len)
            await asyncio.sleep(0.1)

    async def instant_scroll(self):
        # Instantly scrolls down to the bottom of a page.
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
        # This Function will be altered in order to work for multiple websites

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
