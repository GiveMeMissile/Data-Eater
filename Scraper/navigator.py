from Scraper.parser import Judge
import constants as c
import asyncio
import time

##########################################################################
# Defining what will be added:  
# 1: Button Prioritization (based on name) ✓
# 2: Link Prioritization ✓
# 3: Location rework + update usage ✓
# 4: Check for Dead ✓
# 5: Save Websites Scores (from Judge) ✓
# 6: Add Capabilities to handle search bars 
# 7: Add Abilities to return to the previous website with the best score

class Navigator:
    # Class which uses Playwright in order to navigate the internet and get html data to be used by the parser

    def __init__(self, page):

        self.page = page
        self.pages = {"Page": []}
        if self.page.url != "about:blank":
            self.pages["Page"].append(self.page.url)
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
        if not await self.page_already_saved(url):
            self.pages["Page"].append(url)
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

    async def infinite_scroll(self, max_scrolls=c.MAX_SCROLLS):
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
            if not max_scrolls == -1:
                if max_scrolls < num_scrolls:
                    break
            old_height = new_height

    async def return_to_idx(self, idx):
        # Returns the page to a preivious url based off of its location in the locations list
        await self.page["Page"].goto(self.pages["Page"][idx])

    async def get_all_buttons(self):
        # Returns a list of all the buttons contained within the page.
        buttons = await self.page.get_by_role("button").all()
        return buttons

    async def get_all_links(self):
        # Returns a list of all the links contained within the page.
        links = await self.page.get_by_role("link").all()
        return links
    
    async def page_already_saved(self, url):
        # Checks if a page has already been saved...
        for page_url in self.pages["Page"]:
            if page_url == url:
                return True
        return False
    
    async def click_all(self, button=True):
        # Clicks on all of the buttons or links and checks for the changes in the website.
        w = await self.wait_for_delay()
        previous_page = self.pages["Page"][len(self.pages["Page"]) - 1]
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
                self.pages["Page"].append(self.page.url)
                await self.goto(previous_page)


class Analyzer(Navigator):
    # This class is focused on getting information about the page

    def __init__(self, page, words, samples):
        super().__init__(page)
        self.judge = Judge()
        self.samples = []
        for part in samples:
            self.samples += part.split(" ")
        self.words = words
        self.pages["scraping"] = []
        self.pages["exploration"] = []
        self.save_page_score(self.page.url)

    async def get_all_buttons(self):
        # Gets all links and counts the exploration score from links

        score = 0
        buttons = await super().get_all_buttons()
        prioritized_list = []
        for button in buttons:
            name = await button.inner_text()
            if any(priority in name for priority in (c.MAX_PRIORITY + self.words)):
                prioritized_list.append(button)
                score += 0.1
        
        for button in buttons:
            name = await button.inner_text()
            if any(priority in name for priority in (c.NORMAL_PRIORITY + self.samples)):
                prioritized_list.append(button)
                score += 0.05
        
        for button in buttons:
            if any(button == b for b in prioritized_list):
                continue
            name = await button.inner_text()
            if not any(reject in name for reject in c.REJECT):
                prioritized_list.append(button)
                score += 0.025

        return prioritized_list, score
    
    async def get_all_links(self):
        # Gets all links and counts the exploration score from links

        score = 0
        links = await super().get_all_links()
        prioritized_list = []
        for link in links:
            text = await link.inner_text()
            if any(priority in text for priority in (c.MAX_PRIORITY + self.words)):
                prioritized_list.append(link)
                score += 0.1
        
        for link in links:
            text = await link.inner_text()
            if any(priority in text for priority in (c.NORMAL_PRIORITY + self.samples)):
                prioritized_list.append(link)
                score += 0.05
        
        for link in links:
            text = await link.inner_text()
            if any(link == b for b in prioritized_list):
                continue
            if not any(reject in text for reject in c.REJECT):
                prioritized_list.append(link)
                score += 0.025

        return prioritized_list, score

    async def check_infinite_scroll(self):
        # Checks if a page is infinitely scrollable. 

        old_height = await self.page.evaluate("document.body.scrollHeight")
        await self.mouse_scroll(old_height)
        new_height = await self.page.evaluate("document.body.scrollHeight")
        await asyncio.sleep(0.5)
        if new_height > old_height:
            return True
        return False
    
    async def goto(self, url):
        # Go to a different page and saves its exploration and scraping score. 

        exists = await super().goto(url)
        if not exists:
            return exists
        await asyncio.sleep(0.1)
        if not await self.page_already_saved(url):
            await self.save_page_score(url)
        return exists
    
    async def save_page_score(self, url):
        self.pages["scraping"].append(self.judge.get_score(url, await self.get_html()))
        _, score_1 = await self.get_all_buttons()
        _, score_2 = await self.get_all_links()
        self.pages["exploration"].append(score_1 + score_2)
    
    async def is_dead_end(self):
        # Checks if a page has no links/buttons to use to navigate to other pages.

        _, score_1 = await self.get_all_buttons()
        _, score_2 = await self.get_all_links()
        if score_1 + score_2 == 0:
            return True
        return False

class Explorer(Analyzer):
    def __init__(self, page, words, samples):
        super().__init__(page, words, samples)
        self.pages["scraped"] = []
        self.pages["explored"] = []
        self.pages["scraped"][0] = False
        self.pages["explored"][0] = False

    async def scrape_page(self, idx=None):
        # Scrapes the page, that bout it...

        if idx is not None:
            await self.return_to_idx(idx)
            self.pages["scraped"][idx] = True
        else:
            self.pages["scraped"][len(self.pages["scraped"]) - 1] = True
        if not self.judge.is_valid(self.page.url, await self.get_html()):
            return None
        if await self.check_infinite_scroll():
            await self.infinite_scroll()
        return self.judge.get_text_samples(await self.get_html())
        
    