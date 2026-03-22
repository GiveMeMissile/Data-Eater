import constants as c
import asyncio
import time

############################
# Functions to be added:
# 1: Add Request Limit ✓
# 2: Scrolling Function 
# 3: Get All Buttons On a screen (parser?)
# 4: Get All links On a screen
# 5: Determine if a page has data to be harvested.
# 6: 

class Navigator:
    # Class which uses Playwright in order to navigate the internet and get html data to be used by the parser

    def __init__(self, page):
        self.page = page
        self.locations = []
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

    async def return_to_idx(self, idx):
        # Returns the page to a preivious url based off of its location in the locations list

        await self.page.goto(self.locations[idx])

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
